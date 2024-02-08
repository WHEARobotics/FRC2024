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
        boxes_batch = batch['boxes'].cpu().numpy()
        targets = torch.from_numpy(bboxes_to_prediction_array(boxes_batch)).to(device)

        # Forward pass
        predictions = model(input_images)
        # Compute loss
        loss = loss_function(predictions, targets)

        DEBUG_BOXES = True
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
        loss.backward()  # Computes the derivative of the loss w.r.t. the parameters
        optimizer.step()  # Updates the parameters

        return loss
def train(num_epochs, device, model, optimizer, loss_function, dataloader):
    for epoch in range(num_epochs):
        print("Epoch", epoch + 1)
        loss = train_one_epoch(epoch, device, model, optimizer, loss_function, dataloader)
        print(f'Epoch [{epoch + 1}/{num_epochs}], Loss: {loss.item()}')

def main(device, imgs_df, anns_df, img_dir, train_dir):
    model = SharkVision().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    #loss_function = torchvision.ops.generalized_box_iou_loss
    loss_function = nn.MSELoss()
    train_ds = NotesDataset(imgs_df, anns_df, img_dir)
    train_dl = DataLoader(train_ds, batch_size=16, shuffle=True, num_workers=4, persistent_workers = False)
    num_epochs = 5
    train(num_epochs, device, model, optimizer, loss_function, train_dl)

if __name__ == '__main__':
    mp.set_start_method("spawn", force=True)
    mp.set_sharing_strategy('file_system')
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