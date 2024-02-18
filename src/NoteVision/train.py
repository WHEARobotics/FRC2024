import os
from PIL import Image
import torch
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from cocohelper import COCOHelper
import torch.multiprocessing as mp
import torch.nn as nn
from torchinfo import summary
import torchvision
import math
import numpy as np
import time
import mlflow

from notesdataset import NotesDataset
from sharkvision import SharkVision

def bbox_to_prediction_values(bbox):
    # TODO: These need to be configurable and come from resolution of the dataloader image tensor
    prediction_box_width = 640 / 10
    prediction_box_height = 640 / 10
    x_prediction_box = math.floor(bbox[0] / prediction_box_width)
    y_prediction_box = math.floor(bbox[1] / prediction_box_height)
    prediction_box = (x_prediction_box, y_prediction_box)
    bbox_center = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)
    bbox_offset = (bbox[0] - bbox_center[0], bbox[1] - bbox_center[1])
    bbox_scale = (bbox[2] / 100.0, bbox[3] / 100.0)
    return prediction_box, bbox_offset, bbox_scale

def bboxes_to_prediction_array(bboxes):
    batch_size = bboxes.shape[0]

    prediction_array = np.zeros((batch_size, 500))
    n = 10
    for batch_ix in range(batch_size):
        ix = 0
        if len(bboxes[batch_ix]) > 0:
            #print("Made a detection")
            for col in range(n):
                for row in range(n):
                    for bbox in bboxes[batch_ix]:
                        # Filter out dummy boxes
                        if bbox[0] != -1:
                            prediction_box, offset_vals, scale_vals = bbox_to_prediction_values(bbox)
                            if row == prediction_box[0] and col == prediction_box[1] :
                                prediction_array[batch_ix][ix] = 1
                                prediction_array[batch_ix][ix + 1] = offset_vals[0]
                                prediction_array[batch_ix][ix + 2] = offset_vals[1]
                                prediction_array[batch_ix][ix + 3] = scale_vals[0]
                                prediction_array[batch_ix][ix + 4] = scale_vals[1]
                            else:
                                # Already zero, so no need to set it
                                pass
                        else:
                            # Already zero, so no need to set it
                            pass
                    ix += 5
    return prediction_array

def train_one_epoch(epoch, device, model, optimizer, loss_function, dataloader):
    for batch_ix, batch in enumerate(dataloader):
        print(".", end="", flush=True)
        input_images = batch['image']
        assert input_images.sum() > 0
        boxes_batch = batch['boxes'].float().cpu().numpy()
        assert boxes_batch.sum() != 0
        targets = torch.from_numpy(bboxes_to_prediction_array(boxes_batch)).to(device).float()

        # Forward pass
        predictions = model(input_images).float()
        # Compute loss
        loss = loss_function(predictions, targets).float()

        DEBUG_BOXES = False
        if DEBUG_BOXES:
            # Get the first set of targets in the batch
            target = boxes_batch[0]
            # Get the first set of predictions in the batch
            prediction = predictions[0].detach().cpu().numpy()
            #Convert the prediction back to a box
            prediction_boxes = []
            for i in range(0, 500, 5):
                if prediction[i] > 0.8:
                    x = prediction[i + 1] * 100
                    y = prediction[i + 2] * 100
                    w = prediction[i + 3] * 100
                    h = prediction[i + 4] * 100
                    prediction_boxes.append([x, y, w, h])
            if len(prediction_boxes) > 0:
                print("Prediction boxes", prediction_boxes)
                print("Target boxes", target)


        # Backward pass and optimize
        optimizer.zero_grad()  # Clears old gradients from the last step
        assert loss.dtype == torch.float32
        assert targets.dtype == torch.float32
        assert predictions.dtype == torch.float32
        loss.backward()  # Computes the derivative of the loss w.r.t. the parameters
        optimizer.step()  # Updates the parameters
        if batch_ix % 100 == 0:
            print(f"Batch {batch_ix} loss {loss.item():.2f}")
            mlflow.log_metric("loss", loss.item())
            box_yes_no_f1 = calculate_box_yes_no_f1(predictions, targets)
            mlflow.log_metric("box_yes_no_f1", box_yes_no_f1)

    return loss

def calculate_box_yes_no_f1(predictions, targets):
    # The predictions and targets are a tensor of shape (batch_size, 500)
    # The box yes/no f1 score is the f1 score of the yes/no classification
    # for each of the 100 boxes, which occur every 5 elements in the tensor
    # The first element is the yes/no classification, and the next 4 elements
    # are the offset and scale values

    # The f1 score is the harmonic mean of precision and recall

    # Precision is the number of true positives divided by the number of true positives
    # plus the number of false positives

    # Recall is the number of true positives divided by the number of true positives
    # plus the number of false negatives

    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    for batch_ix in range(predictions.shape[0]):
        prediction = predictions[batch_ix].detach().cpu().numpy()
        target = targets[batch_ix].detach().cpu().numpy()
        for i in range(0, 500, 5):
            if target[i] == 1:
                # This is a box
                if prediction[i] > 0.5:
                    # This is a true positive
                    true_positives += 1
                else:
                    # This is a false negative
                    false_negatives += 1
            else:
                # This is not a box
                if prediction[i] > 0.5:
                    # This is a false positive
                    false_positives += 1
                else:
                    # This is a true negative
                    true_negatives += 1
        

    precision = true_positives / (true_positives + false_positives + 1e-10)
    recall = true_positives / (true_positives + false_negatives + 1e-10)
    f1 = 2 * (precision * recall) / (precision + recall + 1e-10)
    return f1

def train(num_epochs, device, model, optimizer, loss_function, dataloader):
    mlflow.set_tracking_uri("sqlite:///mlruns.db")
    mlflow.set_experiment("SharkVision")
    with mlflow.start_run():
        for epoch in range(num_epochs):
            start = time.time()
            print("Epoch", epoch + 1)
            loss = train_one_epoch(epoch, device, model, optimizer, loss_function, dataloader)
            print(f"Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item()}, duration: {time.time() - start}")

def main(device, imgs_df, anns_df, img_dir, train_dir):
    model = SharkVision().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.00001)
    #loss_function = torchvision.ops.generalized_box_iou_loss
    loss_function = nn.MSELoss()
    train_ds = NotesDataset(imgs_df, anns_df, img_dir)
    train_dl = train_dl = DataLoader(train_ds, batch_size=64, shuffle=True, num_workers=0)
    num_epochs = 50
    train(num_epochs, device, model, optimizer, loss_function, train_dl)

if __name__ == '__main__':
    mp.set_start_method("spawn", force=True)
    mp.set_sharing_strategy("file_system")
    data_dir = Path("/mnt/d/scratch_data/FRC2024")
    assert (os.path.exists(data_dir))

    train_dir = os.path.join(data_dir, "train")
    test_dir = os.path.join(data_dir, "test")
    val_dir = os.path.join(data_dir, "valid")
    assert (os.path.exists(train_dir))
    assert (os.path.exists(test_dir))
    assert (os.path.exists(val_dir))

    train_annotations_file = os.path.join(train_dir, "_annotations.coco.json")

    ch = COCOHelper.load_json(train_annotations_file, train_dir)
    imgs_df = ch.imgs
    anns_df = ch.anns

    img_dir = "/mnt/d/scratch_data/FRC2024/train"

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    main(device, imgs_df, anns_df, img_dir, train_dir)