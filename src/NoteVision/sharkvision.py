import torch.nn as nn
from torchinfo import summary
import torch
import torchvision
import torch.nn.init as init

def weights_relu_init(m):
    if isinstance(m, nn.Linear):
        m.weight = init.kaiming_uniform_(m.weight, mode='fan_in', nonlinearity='relu').float()
        if m.bias is not None:
            m.bias = init.constant_(m.bias, 0).float()
    elif isinstance(m, nn.Conv2d):
        m.weight = init.xavier_normal_(m.weight).float()
        if m.bias is not None:
            m.bias = init.constant_(m.bias, 0).float()

def weights_sigmoid_init(m):
    if isinstance(m, nn.Linear):
        m.weight = init.xavier_normal_(m.weight).float()
        if m.bias is not None:
            m.bias = init.constant_(m.bias, 0).float()
    elif isinstance(m, nn.Conv2d):
        m.weight = init.xavier_normal_(m.weight).float()
        if m.bias is not None:
            m.bias = init.constant_(m.bias, 0).float()

class SharkVision(nn.Module):
    def __init__(self, verbose = False):
        super().__init__()

        conv_blocks = SharkVision.build_conv_blocks()
        weights_relu_init(conv_blocks)
        head  = SharkVision.build_head()
        weights_sigmoid_init(head)
        if verbose == True:
            print("Backbone")
            summary(conv_blocks, (1,3, 640, 640))
            print("\n----------\nHead")
            summary(head, (1,384*5*5))
            print("Backbone")
            summary(conv_blocks, (1,3, 640, 640))
            print("\n----------\nHead")
            summary(head, (1,384*5*5))
        self.net = nn.Sequential(
            conv_blocks,
            # Flatten the output of the last convolutional layer so it can be fed into the head
            nn.Flatten(),
            head
        )

    @staticmethod
    def build_conv_blocks():
        conv_blocks = nn.Sequential()
        conv_blocks.add_module("block_0", SharkVision.build_block(3))
        conv_blocks.add_module("block_1", SharkVision.build_block(6))
        conv_blocks.add_module("block_2", SharkVision.build_block(12))
        conv_blocks.add_module("block_3", SharkVision.build_block(24))
        conv_blocks.add_module("block_4", SharkVision.build_block(48))
        conv_blocks.add_module("block_5", SharkVision.build_block(96))
        conv_blocks.add_module("block_6", SharkVision.build_block(192))
        return conv_blocks

    @staticmethod
    def build_block(in_channels):
        out_channels = in_channels * 2
        kernel_size = (3, 3)
        conv = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            padding=1,
            padding_mode="zeros"
        )
        norm = torch.nn.BatchNorm2d(out_channels)
        pool = torch.nn.MaxPool2d((2, 2))
        activation = torch.nn.ReLU()
        block = nn.Sequential()
        block.add_module("conv", conv)
        block.add_module("activation", activation)
        block.add_module("pool", pool)
        return block

    @staticmethod
    def build_head():
        # Kind of arbitrary, but should be more than enough
        out_features = 1024

        # This need to correspond to the shape of the final convolution layer
        # This will be the correct shape if the input image is 640x640
        linear_0 = nn.Linear(384 * 5 * 5, out_features)

        # Output represents a patch of size 1/n^2 the input image
        n = 10
        output_shape = n * n * 5

        linear_1 = nn.Linear(1024, output_shape)
        head = nn.Sequential(
            linear_0,
            nn.Sigmoid(),
            linear_1
        )
        return head

    def forward(self, input_image):
        return self.net(input_image)


if __name__ == "__main__":
    model = SharkVision()
    summary(model, (16, 3, 640, 640))