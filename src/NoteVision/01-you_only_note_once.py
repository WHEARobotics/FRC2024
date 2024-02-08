import torch
import torch.multiprocessing as mp
import os
from pathlib import Path
from cocohelper import COCOHelper
from cocohelper.visualizer import COCOVisualizer
import math
import torchvision

# Should only be run once, when kernel (re-)starts, so make a global flag
if 'initialization_done' not in globals():
    multiprocessing_start_method_run = False

if not multiprocessing_start_method_run:
    print("Setting start method to 'spawn'")
    mp.set_start_method("spawn", force=True)
    multiprocessing_start_method_run = True

# Batch Size
bs = 16

resolution = [640,480]

in_channels = 3

out_channels = 6

kernel_size = (3,3)

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.mps.is_available() else "cpu")

dtype = torch.float32

# # Training

num_epochs = 30

# ## Dataloader

train_dir = '/mnt/d/scratch_data/FRC2024/train'

train_annotations_file = os.path.join(train_dir, "_annotations.coco.json")

ch = COCOHelper.load_json(train_annotations_file, train_dir)

ch.imgs

ch.anns

ch.anns.image_id.value_counts().max()

for i in range(0, 20):
    try:
        COCOVisualizer(ch).visualize(img_id=i, show_bbox=True, show_segmentation=True)
    except:
        pass

ch.anns[ch.anns.image_id == 8]

ch.anns[ch.anns.image_id == 19]

# ## All we care about is annotations with `category_id` == 1

ch.imgs[ch.imgs.index==19]

# Grr... so there appears to be no way to recapture the original aspect ratio and pad instead of squish

ch.imgs[ch.imgs.height != 640]

COCOVisualizer(ch).visualize(img_id=22330, show_bbox=True, show_segmentation=True)

COCOVisualizer(ch).visualize(img_id=58155, show_bbox=True, show_segmentation=True)

# False negative in `58155`! There's a note behind his arm!

ch.imgs[ch.imgs.height == 360]

ch.imgs.loc[58155].file_name

# ## Annotation To Prediction

ch.anns[ch.anns.image_id == 58155]

ch.anns[ch.anns.image_id == 58155].bbox

ch.anns[ch.anns.image_id == 58155].bbox.to_numpy()

# `bbox` is clearly x, y, width, height.
#
# So our goal is to map this into:
#
# 1) which prediction box contains the center? 
# 3) What are the x and y offsets?
# 2) what are the x-scale and y-scale multiples?
#
# ### Which prediction box contains the center?
#
# The number of prediction boxes is n^2.

# +
prediction_box_width = resolution[0]/n
prediction_box_height = resolution[1]/n

prediction_box_width, prediction_box_height
# -

bbox = ch.anns.loc[74369].bbox

x_prediction_box = math.floor(bbox[0] / prediction_box_width)
y_prediction_box = math.floor(bbox[1] / prediction_box_height)
x_prediction_box, y_prediction_box

bbox_center = (bbox[0] + bbox[2]/2, bbox[1] + bbox[3]/2)
bbox_center

# +

bbox_offset = (bbox[0] - bbox_center[0], bbox[1] - bbox_center[1])
bbox_offset
# -

# Scale? How about as a multiple of a 100x100 rectangle?
bbox_scale = (bbox[2] / 100.0, bbox[3] / 100.0)
bbox_scale


# +

bbox_to_prediction_values(bbox)


# +

print(bboxes_to_prediction_array(ch.anns[ch.anns.image_id == 58155].bbox.to_numpy()))

# Define the transformation pipeline


# Create the Dataset
dataset = NotesDataset(imgs_df=imgs_df, anns_df=anns_df, img_dir=img_dir)

# Create the DataLoader
dataloader = DataLoader(dataset, batch_size=4, shuffle=True, num_workers=2)

# -

for i, batch in enumerate(dataloader):
    print(i)
    print(batch)
    raise Exception("Stop")
    #images = batch['image']
    #boxes = batch['boxes']
    #labels = batch['labels']
    # Your training code here...






