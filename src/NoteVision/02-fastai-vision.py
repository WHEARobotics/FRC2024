# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: detectron2
#     language: python
#     name: detectron2
# ---

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


# + jupyter={"outputs_hidden": false}
data_dir = Path("/mnt/d/scratch_data/FRC2024")
assert (os.path.exists(data_dir))

train_dir = os.path.join(data_dir, "train")
test_dir = os.path.join(data_dir, "test")
val_dir = os.path.join(data_dir, "valid")
assert (os.path.exists(train_dir))
assert (os.path.exists(test_dir))
assert (os.path.exists(val_dir))


# + [markdown] jupyter={"outputs_hidden": false}
# # Filter out the images that have no annotations
# imgs_with_anns = anns_df["image_id"].unique()
# imgs_df = imgs_df[imgs_df.index.isin(imgs_with_anns)]


# + jupyter={"outputs_hidden": false}
IMG_SIZE = 256
transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
])

# + jupyter={"outputs_hidden": false}
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# -

# Going with `MultiCategoryBlock` for the purposes of the yes-no patch classification

def draw_anns(train_dir, imgs_df, anns_df, fpath):
    fname = Path(fpath).name
    if not os.path.exists(fpath):
        raise Exception(f"Can't find {fpath} in {train_dir}")
    img = PIL.Image.open(fpath)
    matches = imgs_df[imgs_df.file_name == fname].index
    if len(matches) > 0:
        img_id = matches[0]
        anns = anns_df[anns_df.image_id ==img_id].bbox.values
        img_w, img_h = imagesize.get(fpath)
        print(img_w, img_h)
        draw = ImageDraw.Draw(img)
        print(anns)
        print(type(anns))
        print(len(anns))
        for ann in anns:
            x, y, w, h = ann
            draw.rectangle([(x, y), (x+w, y+h)], outline="green", width=1)
    return img


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

all_annotations = {**train_annotations, **valid_annotations}


# -

def patches_for(img_dir, anns_df, image_id, fname):
    label = np.array([])
    # Retrieve bbox values for that image_id
    anns = anns_df[anns_df['image_id'] == image_id]['bbox'].tolist()
    if len(anns) == 0:
        label = np.append(label, "-1")
    # Get the image size
    img_w, img_h = imagesize.get(os.path.join(img_dir, fname))
    for ann in anns:
        x, y, w, h = ann

        x = x / img_w
        y = y / img_h
        w = w / img_w
        h = h / img_h

        center_x = x + w / 2
        center_y = y + h / 2

        grid_x = math.floor(center_x * n)
        grid_y = math.floor(center_y * n)

        patch_number = grid_y * n + grid_x
        if x < n and y < n and patch_number < (n*n):
            label = np.append(label, str(patch_number))
        else:
            print(f"Bad annotation {fname} : {ann}, {img_w}, {img_h}, {patch_number}")
    return label


# +
# %%time 

n = 10 
if not os.path.exists("patches_for_fname.json"):
    #~ 20 minutes! 
    patches_for_fname = {}
    for ann_list in [(train_dir, train_imgs, train_annotations), (val_dir, valid_imgs, valid_annotations)]:
        img_dir, imgs_df, anns_df = ann_list
        pbar = tqdm(len(imgs_df))
        for row in imgs_df.iterrows():
            fname = row[1]["file_name"]
            id = row[0]
            patches = patches_for(img_dir, anns_df, id, fname)
            patches_for_fname[fname] = patches
            pbar.update()
        pbar.close()
    # Convert numpy ndarray to list
    dict_data = {k: v.tolist() for k, v in patches_for_fname.items()}

    # Write to json
    with open('patches_for_fname.json', 'w') as f:
        json.dump(dict_data, f)
else:
    with open("patches_for_fname.json", "r") as f:
        patches_for_fname = json.load(f)

# +
n = 10
#get_y_func = build_get_y(n, train_dir)

vocab = [str(i) for i in range(-1,100)]


# -


def splitter(dataset):
    # Custom splitter based on your dataset's structure
    # For simplicity, let's assume dataset is a list of file paths
    train_files = get_image_files(data_dir/'train')
    valid_files = get_image_files(data_dir/'valid')
    # Convert file paths to indices
    train_idxs = [i for i, o in enumerate(dataset) if o in train_files]
    valid_idxs = [i for i, o in enumerate(dataset) if o in valid_files]
    return train_idxs, valid_idxs


dblock = DataBlock(blocks=(ImageBlock, MultiCategoryBlock(vocab=vocab)),
                 get_items= get_image_files,
                 splitter=splitter,#GrandparentSplitter(train_name="train", valid_name="valid"),
                 get_y = lambda fname : patches_for_fname[Path(fname).name],
                 item_tfms=Resize(256),
                 batch_tfms=aug_transforms())

# %%time 
print(f"Calling dataloaders @ {time.ctime()}")
dls = dblock.dataloaders(data_dir, path=data_dir, num_workers=8)
print(f"Finished at {time.ctime()}")

# + jupyter={"outputs_hidden": false} is_executing=true
dls.show_batch()


# + jupyter={"outputs_hidden": false} is_executing=true
b = dls.one_batch()
b[0].shape, b[1]

# + jupyter={"outputs_hidden": false} is_executing=true
b[0][0].show()

# + jupyter={"outputs_hidden": false} is_executing=true
from fastai.vision.all import *
# -

cbs = [ SaveModelCallback (), ShowGraphCallback(),  ]

# + jupyter={"outputs_hidden": false} is_executing=true

# Default uses BCELoss for multi-label classification, can pass explicitly here, too
learn = vision_learner(dls, resnet34, metrics=partial(accuracy_multi, thresh=0.5), cbs=cbs, pretrained=False)
lr = learn.lr_find()
print(lr)

# + is_executing=true jupyter={"outputs_hidden": false}
learn.fit_one_cycle(5, lr.valley)
# -

learn.save("fastai-vision-1")

img = PIL.Image.open(os.path.join(data_dir, "test", "youtube-9_jpg.rf.ddf5e1650b546877d0ffb55280750fba.jpg"))
img

pred,pred_idx,probs = learn.predict(os.path.join(data_dir, "test", "youtube-9_jpg.rf.ddf5e1650b546877d0ffb55280750fba.jpg"))


pred, probs

int(pred[0])


# +
def drawPatch(img, patch_str, color):
    patch = int(patch_str)
    draw = ImageDraw.ImageDraw(img)
    top = math.floor(patch/10)* 64
    left = (patch/10 - math.floor(patch/10)) * 64 * 10
    bottom = top + 64
    right = left + 64
    top_left_corner = (left, top)
    bottom_right_corner = (right, bottom)
    draw.rectangle([top_left_corner, bottom_right_corner], outline=color, width=3)
    return img

drawPatch(img, 77, "green")
# -

import torchinfo

torchinfo.summary(learn.model)

# ```
# ===============================================================================================
# Layer (type:depth-idx)                        Output Shape              Param #
# ===============================================================================================
# Sequential                                    [16, 101]                 --
# ├─Sequential: 1-1                             [16, 512, 20, 20]         --
# │    └─Conv2d: 2-1                            [16, 64, 320, 320]        9,408
# │    └─BatchNorm2d: 2-2                       [16, 64, 320, 320]        128
# │    └─ReLU: 2-3                              [16, 64, 320, 320]        --
# │    └─MaxPool2d: 2-4                         [16, 64, 160, 160]        --
# │    └─Sequential: 2-5                        [16, 64, 160, 160]        --
# │    │    └─BasicBlock: 3-1                   [16, 64, 160, 160]        73,984
# │    │    └─BasicBlock: 3-2                   [16, 64, 160, 160]        73,984
# │    │    └─BasicBlock: 3-3                   [16, 64, 160, 160]        73,984
# │    └─Sequential: 2-6                        [16, 128, 80, 80]         --
# │    │    └─BasicBlock: 3-4                   [16, 128, 80, 80]         230,144
# │    │    └─BasicBlock: 3-5                   [16, 128, 80, 80]         295,424
# │    │    └─BasicBlock: 3-6                   [16, 128, 80, 80]         295,424
# │    │    └─BasicBlock: 3-7                   [16, 128, 80, 80]         295,424
# │    └─Sequential: 2-7                        [16, 256, 40, 40]         --
# │    │    └─BasicBlock: 3-8                   [16, 256, 40, 40]         919,040
# │    │    └─BasicBlock: 3-9                   [16, 256, 40, 40]         1,180,672
# │    │    └─BasicBlock: 3-10                  [16, 256, 40, 40]         1,180,672
# │    │    └─BasicBlock: 3-11                  [16, 256, 40, 40]         1,180,672
# │    │    └─BasicBlock: 3-12                  [16, 256, 40, 40]         1,180,672
# │    │    └─BasicBlock: 3-13                  [16, 256, 40, 40]         1,180,672
# │    └─Sequential: 2-8                        [16, 512, 20, 20]         --
# │    │    └─BasicBlock: 3-14                  [16, 512, 20, 20]         3,673,088
# │    │    └─BasicBlock: 3-15                  [16, 512, 20, 20]         4,720,640
# │    │    └─BasicBlock: 3-16                  [16, 512, 20, 20]         4,720,640
# ├─Sequential: 1-2                             [16, 101]                 --
# │    └─AdaptiveConcatPool2d: 2-9              [16, 1024, 1, 1]          --
# │    │    └─AdaptiveMaxPool2d: 3-17           [16, 512, 1, 1]           --
# │    │    └─AdaptiveAvgPool2d: 3-18           [16, 512, 1, 1]           --
# │    └─Flatten: 2-10                          [16, 1024]                --
# │    └─BatchNorm1d: 2-11                      [16, 1024]                2,048
# │    └─Dropout: 2-12                          [16, 1024]                --
# │    └─Linear: 2-13                           [16, 512]                 524,288
# │    └─ReLU: 2-14                             [16, 512]                 --
# │    └─BatchNorm1d: 2-15                      [16, 512]                 1,024
# │    └─Dropout: 2-16                          [16, 512]                 --
# │    └─Linear: 2-17                           [16, 101]                 51,712
# ===============================================================================================
# Total params: 21,863,744
# Trainable params: 21,863,744
# Non-trainable params: 0
# Total mult-adds (G): 478.47
# ===============================================================================================
# Input size (MB): 78.64
# Forward/backward pass size (MB): 7812.17
# Params size (MB): 87.45
# Estimated Total Size (MB): 7978.26
# ===============================================================================================
# ```


