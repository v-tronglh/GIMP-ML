import numpy as np
import torch
from PIL import Image, ImageDraw
from torchvision import transforms
from torchvision.models.segmentation import fcn_resnet101

CLASS_COLORS = [
    (0, 0, 0),  # background
    (6, 150, 104),  # aeroplane
    (144, 234, 102),  # bicycle
    (34, 79, 62),  # bird
    (28, 224, 178),  # boat
    (147, 224, 240),  # bottle
    (49, 89, 185),  # bus
    (213, 208, 250),  # car
    (162, 97, 246),  # cat
    (251, 172, 246),  # chair
    (113, 31, 134),  # cow
    (141, 127, 149),  # diningtable
    (11, 41, 208),  # dog
    (249, 13, 160),  # horse
    (198, 95, 167),  # motorbike
    (79, 66, 86),  # person
    (5, 157, 197),  # pottedplant
    (205, 219, 155),  # sheep
    (112, 159, 15),  # sofa
    (110, 57, 1),  # train
    (254, 143, 6),  # tvmonitor
]


class FCNSemSeg:
    def __init__(self, im_size=128, device='cpu'):
        self.im_size = im_size
        self.device = device
        self.model = fcn_resnet101(pretrained=True, pretrained_backbone=False).to(device).eval()

    def preprocess(self, img):
        transform = transforms.Compose([
            transforms.Resize(size=(self.im_size, self.im_size)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        img = transform(img)
        return img

    def postprocess(self, tensor, org_size=None):
        seg_mask = Image.new('RGB', tensor.shape[-1::-1], (0, 0, 0))
        drawing = ImageDraw.Draw(seg_mask)
        transform = transforms.ToPILImage()

        for i, color in enumerate(CLASS_COLORS):
            mask = transform((tensor == i).to(torch.float32))
            drawing.bitmap((0, 0), mask, fill=color)

        if org_size is not None:
            seg_mask = seg_mask.resize(org_size, resample=Image.NEAREST)

        seg_mask = np.array(seg_mask)
        return seg_mask

    def __call__(self, img):
        width, height = img.shape[1::-1]
        img = Image.fromarray(img).convert('RGB')
        img = self.preprocess(img)
        img = img.to(self.device)
        img = img.unsqueeze(0)

        with torch.no_grad():
            img = self.model(img)['out']
            img = img.squeeze(0)
            img = img.max(dim=0).indices.cpu()

        img = self.postprocess(img, org_size=(width, height))
        return img
