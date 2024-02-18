import os
from PIL import Image
import torch
from pathlib import Path
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from cocohelper import COCOHelper
import torch.multiprocessing as mp
from torch.nn.utils.rnn import pad_sequence

class ResizeAndPad:
    def __init__(self, size, fill=0, padding_mode='constant'):
        self.size = size
        self.fill = fill
        self.padding_mode = padding_mode

    def __call__(self, img):
        original_size = img.size
        # Calculate the size for resizing
        ratio = self.size / max(img.size)
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))

        # Resize the image
        img = transforms.Resize(new_size)(img)

        # Calculate padding
        pad_height = (self.size - new_size[1]) // 2
        pad_width = (self.size - new_size[0]) // 2

        # Pad the image
        img = transforms.Pad((pad_width, pad_height, pad_width, pad_height), fill=self.fill,
                             padding_mode=self.padding_mode)(img)

        # If the size is odd, we might be off by one pixel, so resize one last time
        img = transforms.Resize((self.size, self.size))(img)
        assert img.size == (self.size, self.size)

        return img


class NotesDataset(Dataset):
    def __init__(self, imgs_df, anns_df, img_dir):
        """
        Args:
            imgs_df (DataFrame): DataFrame containing image info.
            anns_df (DataFrame): DataFrame containing annotations.
            img_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied on a sample.
        """
        self.imgs_df = imgs_df
        self.anns_df = anns_df
        self.img_dir = img_dir
        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    def __len__(self):
        return len(self.imgs_df)

    def __getitem__(self, idx):
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # Get image info
        img_name = os.path.join(self.img_dir, self.imgs_df.iloc[idx].file_name)
        with Image.open(img_name) as image:
            image = image.convert('RGB')
            transform = transforms.Compose([
                ResizeAndPad(size=640),
                transforms.ToTensor(),  # Convert image to a tensor
                #transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize the pixel values
            ])
            image_tensor = transform(image).to(self.device)
            assert image_tensor.shape == (3, 640, 640)
            assert image_tensor.sum() > 0
        image.close()

        #img_id = self.imgs_df.iloc
        img_id = idx #self.imgs_df.iloc[idx].id

        # Get notes (category 1) for this image
        img_anns = self.anns_df[(self.anns_df.image_id == img_id) & (self.anns_df.category_id == 1)]
        boxes = img_anns.bbox.tolist() # bbox is a list [x_min, y_min, width, height]

        MAX_NUM_BOXES = 11  # By inspection of the data in the training set
        # Initialize a tensor for boxes with the shape (11, 4), filled with zeros or another placeholder
        boxes_tensor = torch.full((MAX_NUM_BOXES, 4),-1.0).to(self.device)  # Placeholder tensor

        # If there are boxes, copy them into the boxes_tensor
        if len(boxes) > 0:
            real_boxes_tensor = torch.tensor(boxes[:MAX_NUM_BOXES], dtype=torch.float32).to(self.device)  # Get real boxes, ensure no more than MAX_NUM_BOXES
            boxes_tensor[:len(real_boxes_tensor)] = real_boxes_tensor  # Replace parts of the boxes_tensor with real boxes

        labels = img_anns.category_id

        # Assert that the image_tensor contains at least one non-zero pixel
        if image_tensor.sum() == 0:
            print(f"Image tensor is all zeros for image {img_id}, {img_name}")
            assert image_tensor.sum() > 0
        if boxes_tensor.sum() == 0:
            print(f"Boxes tensor is all zeros for image {img_id}")
            assert boxes_tensor.sum() != 0

        sample = {'image': image_tensor, 'boxes': boxes_tensor}

        if len(img_anns) > 0:
            pass
        else:
            # No image annotations (category 1)
            pass

        return sample

if __name__ == '__main__':
    mp.set_start_method("spawn", force=True)
    torch.multiprocessing.set_sharing_strategy('file_system')
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

    img_dir = '/mnt/d/scratch_data/FRC2024/train'
    train_ds = NotesDataset(imgs_df, anns_df, img_dir)
    # Using multiple workers leads to file leaks (for some reason)
    train_dl = DataLoader(train_ds, batch_size=64, shuffle=True, num_workers=0)#, persistent_workers = True, drop_last=True)

    for i, batch in enumerate(train_dl):
        print(f"{i} ", end="", flush=True)
        if i % 100 == 0:
            print(f"Open files: {len(os.listdir('/proc/self/fd'))}")

