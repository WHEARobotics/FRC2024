# +
import fastai

from fastcore.foundation import L

from PIL import ImageDraw

from functools import partial

import os
from PIL import Image
import torch
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from cocohelper import COCOHelper
import torch.multiprocessing as mp
from torch.nn.utils.rnn import pad_sequence
import os
from PIL import Image
import torch
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from cocohelper import COCOHelper

from fastai.metrics import Metric
import torch
import torch.multiprocessing as mp
import torch.nn as nn
from torchinfo import summary
import torchvision
import math
import numpy as np
import time
import mlflow
import torch.nn as nn
from torchinfo import summary
import torch
import torchvision
import torch.nn.init as init

from fastai.data.all import *
from fastai.vision.all import *

import imagesize
import PIL
from tqdm import tqdm

import json
    
import math
import torchinfo


# +
data_dir = Path("/mnt/d/scratch_data/FRC2024")
assert (os.path.exists(data_dir))

train_dir = os.path.join(data_dir, "train")
test_dir = os.path.join(data_dir, "test")
val_dir = os.path.join(data_dir, "valid")
assert (os.path.exists(train_dir))
assert (os.path.exists(test_dir))
assert (os.path.exists(val_dir))
# -


IMG_SIZE = 256
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

# Number of patches per dimension
S = 10

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ## Training data load

# +
# %%time 

train_annotations_file = os.path.join(train_dir, "_annotations.coco.json")

ch = COCOHelper.load_json(train_annotations_file, train_dir)
train_imgs = ch.imgs
train_annotations = ch.anns

val_annotations_file = os.path.join(val_dir, "_annotations.coco.json")
ch = COCOHelper.load_json(val_annotations_file, val_dir)
valid_imgs = ch.imgs
valid_annotations = ch.anns 


imgs_dfs = {
    'train': train_imgs,
    'valid': valid_imgs
}

anns_dfs = {
    'train': train_annotations,
    'valid': valid_annotations
}
# -

train_imgs.head()

train_annotations.head()


# ## Build data structure

# +
def bbox_to_patch_offset(S, patch_dimension, bbox):
    x, y, width, height = bbox
    #print(f"bbox {bbox}")

    center_x = x + width / 2
    center_y = y + height / 2
    #print(f"{y}, {height}, {center_y}")
    row_y = math.floor(center_y / patch_dimension) 
    patch_y = row_y * S
    #print(f"row_y {row_y} patch_y {patch_y} S {S} patch_dimension {patch_dimension}")
    
    x_patch_offset = math.floor(center_x / patch_dimension)
    #print(f"x_patch_offset { x_patch_offset}")
    patch = patch_y + x_patch_offset
    #print(f"patch {patch}")
    assert patch > -1
    if not patch < S**2:
        # print(f"Error with patch calculations:")
        # print(f"bbox {bbox}")
        # print(f"{y}, {height}, {center_y}")
        # print(f"row_y {row_y} patch_y {patch_y} S {S} patch_dimension {patch_dimension}")
        # print(f"x_patch_offset { x_patch_offset}")
        # print(f"patch {patch}")
        patch = -1
    assert patch < S**2


    patch_left = x_patch_offset * patch_dimension
    #print(f"x position of patch left {patch_left}")
    delta_x = x - patch_left
    #print(f"delta_x {delta_x}")
    left_offset_pct = delta_x / patch_dimension
    #print(f"left_offset_pct {left_offset_pct}")
    width_pct = width / patch_dimension

    patch_top = row_y * patch_dimension
    delta_y = y - patch_top
    #print(f"delta_y {delta_y}")
    top_offset_pct = delta_y / patch_dimension
    #print(f"top_offset_pct {top_offset_pct}")
    height_pct = height / patch_dimension

    return [patch, left_offset_pct, top_offset_pct, width_pct, height_pct]

def ann_to_offsets(S : int, img_df : pd.DataFrame, anns_df : pd.DataFrame, filename: str):
    # offsets are relative from the patch top-left (i.e., floor(patch / 10) * patch_dimension for y, remainder for x)
    # Since I know indexes to be unique, I can just grab the first value in the returned Series
    img_id = img_df[img_df.file_name == filename].index[0]
    row = img_df[img_df.file_name == filename].values[0]
    #license, file_name, height, width, date_captured, extra = row
    _, _, height, width, _, _ = row
    patch_dimension = max(height, width) / S

    offsets = []
    anns = anns_df[anns_df.image_id == img_id]
    for idx, ann in anns.iterrows():
        bbox = ann.bbox
        patch_offset = bbox_to_patch_offset(S, patch_dimension, bbox)
        offsets.append(patch_offset)
    
    return offsets


# -

# If the width of the thing is 88 and it starts at 479, it's center is 523. That's patch 8.17. Left is -33 pixels from patch left. So that is -0.515 patch widths from left border. This is born out in the following with `img_id = 2`

for img_id in [
    "20240108_011352_mp4-23_jpg.rf.000f01471da18c54c69a0c258a31b427.jpg", 
    "C41_jpeg_jpg.rf.001a0c8dc40eb33806393f2381f14f4a.jpg",
    "y2mate_com-2024-Field-Tour-Video-Amp_1080p_mp4-84_jpg.rf.001a963f3fc9592bca95e1b8996a7417.jpg", 
    "youtube-398_jpg.rf.002d601487e08744ae89f92dcde13079.jpg", 
    "20240108_012214_mp4-53_jpg.rf.001aace6d451cddaced87cda32be7871.jpg"]:
    offsets = ann_to_offsets(S, train_imgs, train_annotations, img_id)
    print(f"{img_id} -> {offsets}\n----------\n\n")

vocab = [str(i) for i in range(-1,S**2)]

def splitter(dataset):
    #print("Warning: splitter is using 10000 files only")
    dataset = dataset
    # Custom splitter based on your dataset's structure
    # For simplicity, let's assume dataset is a list of file paths
    train_files = get_image_files(data_dir/'train')
    valid_files = get_image_files(data_dir/'valid')
    # Convert file paths to indices
    train_idxs = []
    valid_idxs = []
    for i, o in tqdm(enumerate(dataset)):
        if i % 100 == 0:
            print(f".", end="", flush=True)
        if o in train_files:
            train_idxs.append(i)
        if o in valid_files:
            valid_idxs.append(i)
    return train_idxs, valid_idxs


# ## Bounding box dataloader instead of old `MultiCategoryBlock`

anns = ann_to_offsets(S, train_imgs, train_annotations, "20240108_012527_mp4-69_jpg.rf.0025bc611b972c638cc5aa5b74fc2cf5.jpg")
anns


# +
def tensor_for_anns(anns):
    yolo_tensor = torch.zeros((500,))
    for ann in anns:
        patch, x_offset, y_offset, bbox_width, bbox_height = ann
        offset = patch * 5
        yolo_tensor[offset] = 1
        yolo_tensor[offset + 1] = x_offset
        yolo_tensor[offset + 2] = y_offset
        yolo_tensor[offset + 3] = bbox_width
        yolo_tensor[offset + 4] = bbox_height
    return yolo_tensor

tensor_for_anns(anns)


# -

# Note captures imgs_dfs and anns_dfs (TODO: build )
def yolo_data_for_path(path):
    parent = Path(path).parent.name
    img_df = imgs_dfs[parent]
    ann_df = anns_dfs[parent]
    anns = ann_to_offsets(S, img_df, ann_df, path.name)
    ann_tensor = tensor_for_anns(anns)
    return ann_tensor
    


# Define your DataBlock
dblock = DataBlock(blocks=(ImageBlock, TransformBlock()),
                   get_items=get_image_files, 
                   splitter=splitter,
                   get_y= yolo_data_for_path,
                   item_tfms = Resize(IMG_SIZE),
                   batch_tfms = aug_transforms())

# +
# %%time 
print("Beginning dls load")
start = time.time()
dls = dblock.dataloaders(data_dir, path=data_dir, num_workers=8)
print(f"Finished dls load in {time.time() - start} seconds")
# -

b = dls.one_batch()

b[1].shape


# ## YOLO-like loss function

# +
class CustomYOLOLoss(nn.Module):
    def __init__(self, lambda_coord=5, lambda_noobj=0.5, S=10):
        super(CustomYOLOLoss, self).__init__()
        self.lambda_coord = lambda_coord
        self.lambda_noobj = lambda_noobj
        self.S = S
        self.mse_loss = nn.MSELoss(reduction="sum")  # Summed MSE for accumulated error

    def forward(self, predictions, targets):
        # Reshape targets and predictions to [batch_size, S, S, 5]
        predictions = predictions.view(-1, self.S, self.S, 5)
        targets = targets.view(-1, self.S, self.S, 5)
        
        # Object mask: 1 if object in cell, 0 otherwise
        obj_mask = targets[..., 0] > 0  # Assuming objectness score > 0 indicates presence
        
        # No object mask
        no_obj_mask = targets[..., 0] == 0
        
        # Objectness loss
        obj_loss = self.mse_loss(predictions[..., 0][obj_mask], targets[..., 0][obj_mask])
        
        # No-object loss
        no_obj_loss = self.mse_loss(predictions[..., 0][no_obj_mask], targets[..., 0][no_obj_mask])
        
        # Bounding box loss (for cells with objects only)
        bbox_loss = self.mse_loss(predictions[..., 1:][obj_mask], targets[..., 1:][obj_mask])
        
        # Combining the losses
        loss = self.lambda_coord * bbox_loss + obj_loss + self.lambda_noobj * no_obj_loss
        return loss / predictions.size(0)  # Average loss per batch item

# Example usage
S = 10  # Grid size
batch_size = 2  # Example batch size
model_output = torch.randn(batch_size, 5*S*S)  # Simulated model output
ground_truth = torch.randn(batch_size, 5*S*S)  # Simulated ground truth

loss_fn = CustomYOLOLoss()
loss = loss_fn(model_output, ground_truth)
print(f"Loss: {loss.item()}")

# -

# ## Custom head

num_outputs = 5 * 10**2  # As per the YOLO-style output
model = create_vision_model(resnet34, n_out=num_outputs,cut=-2)

# ## Custom loss



class GIoUWithObjectnessMetric(Metric):
    def __init__(self):
        self.reset()

    def reset(self):
        self.total_giou = 0
        self.total_classification_error = 0
        self.count = 0

    def accumulate(self, learn):
        preds, targs = learn.pred, learn.y
        # Assuming preds and targs are both [batch_size, 5*S^2]
        # And the first element in each 5-vector is the objectness score

        batch_size = preds.shape[0]
        S_squared = preds.shape[1] // 5
        preds = preds.view(batch_size, S_squared, 5)
        targs = targs.view(batch_size, S_squared, 5)

        objectness_preds = preds[..., 0]
        objectness_targs = targs[..., 0]
        giou_preds = preds[..., 1:]
        giou_targs = targs[..., 1:]

        # Compute objectness classification error (simple binary classification for this example)
        classification_error = torch.abs(objectness_preds - objectness_targs).mean()

        # Compute GIoU for correctly classified object presence
        # Note: You'll need to implement or use a GIoU computation function here
        correct_mask = objectness_targs > 0.5  # Assuming threshold of 0.5 for presence
        giou = compute_giou(giou_preds[correct_mask], giou_targs[correct_mask])  # Placeholder

        self.total_giou += giou.sum()
        self.total_classification_error += classification_error.sum()
        self.count += batch_size

    def value(self):
        if self.count == 0: return None
        avg_giou = self.total_giou / self.count
        avg_classification_error = self.total_classification_error / self.count
        # Combine or return separately based on your requirement
        return {'avg_giou': avg_giou, 'avg_classification_error': avg_classification_error}


import torch


def compute_giou(preds, targets):
    # preds and targets format: [x_center, y_center, width, height]

    # Convert [x_center, y_center, width, height] to [x1, y1, x2, y2]
    preds_x1 = preds[:, 0] - preds[:, 2] / 2
    preds_y1 = preds[:, 1] - preds[:, 3] / 2
    preds_x2 = preds[:, 0] + preds[:, 2] / 2
    preds_y2 = preds[:, 1] + preds[:, 3] / 2

    targets_x1 = targets[:, 0] - targets[:, 2] / 2
    targets_y1 = targets[:, 1] - targets[:, 3] / 2
    targets_x2 = targets[:, 0] + targets[:, 2] / 2
    targets_y2 = targets[:, 1] + targets[:, 3] / 2

    # Intersection area
    inter_area = (torch.min(preds_x2, targets_x2) - torch.max(preds_x1, targets_x1)).clamp(0) * \
                 (torch.min(preds_y2, targets_y2) - torch.max(preds_y1, targets_y1)).clamp(0)

    # Union area
    preds_area = (preds_x2 - preds_x1) * (preds_y2 - preds_y1)
    targets_area = (targets_x2 - targets_x1) * (targets_y2 - targets_y1)
    union_area = preds_area + targets_area - inter_area

    # IoU
    iou = inter_area / union_area

    # Enclosing box
    enc_x1 = torch.min(preds_x1, targets_x1)
    enc_y1 = torch.min(preds_y1, targets_y1)
    enc_x2 = torch.max(preds_x2, targets_x2)
    enc_y2 = torch.max(preds_y2, targets_y2)
    enc_area = (enc_x2 - enc_x1) * (enc_y2 - enc_y1)

    # GIoU
    giou = iou - (enc_area - union_area) / enc_area

    return giou


# ## TODO: Modify pre-trained vision learner

cbs = [ SaveModelCallback ()]
learn = Learner(dls, model, loss_func=CustomYOLOLoss(), cbs=cbs, metrics=[GIoUWithObjectnessMetric])

# ## Train

lr = learn.lr_find()
print(lr)

learn.fit_one_cycle(50, lr.valley)

import matplotlib.pyplot as plt

# Plot losses
learn.recorder.plot_loss()
plt.savefig('training_validation_loss.png')  # Save the loss plot

# If you have other metrics aside from loss, plot them
if hasattr(learn.recorder, 'plot_metrics'):
    learn.recorder.plot_metrics()
    plt.savefig('training_metrics.png')  # Save the metrics plot

