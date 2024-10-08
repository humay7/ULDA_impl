"""
https://github.com/gidariss/FewShotWithoutForgetting/blob/master/dataloader.py
"""
import os
import numpy as np
from PIL import Image
from skimage import io
from sklearn.utils import shuffle
import unittest

import torch
import torch.nn as nn
from torch.utils.data import Dataset

from preprocess.tools import read_csv, load_csv2dict

import sys
import warnings
warnings.filterwarnings('ignore')
sys.dont_write_bytecode = True

def PIL_loader(path):
    # open path as file to avoid ResourceWarning (https://github.com/python-pillow/Pillow/issues/835)
    with open(path, 'rb') as f:
        with Image.open(f) as img:
            return img.convert('RGB')

def Default_loader(path):
    return io.imread(path)

def RGB_loader(path):
    return Image.open(path).convert('RGB')

def Gray_loader(path):
    return Image.open(path).convert('L')

class BaseDataSet(Dataset):
    def __init__(self, cfg, transform=None, phase='train', loader=RGB_loader):
        super(BaseDataSet, self).__init__()
        self.phase = phase
        self.transform = transform
        self.loader = loader

        self.way_num = cfg.datasets.way_num
        self.shot_num = cfg.datasets.shot_num
        self.query_num = cfg.datasets.query_num
        self.data_root = cfg.datasets.root

        assert (phase in ['train', 'val', 'test'])

        print('Loading normal dataset - phase {0}'.format(phase))
        if phase == 'train':
            self.csv_path    = cfg.datasets.train_data_dir
        elif phase == 'val':
            self.csv_path    = cfg.datasets.val_data_dir
        elif phase == 'test':
            self.csv_path    = cfg.datasets.test_data_dir
        else:
            raise ValueError('phase ought to be in [train/test/val]')

        self.data_list = read_csv(self.csv_path)
        self.class_img_dict, class_list = load_csv2dict(self.csv_path)
        self.class_list = sorted(list(class_list))
        self.label2Int = {item: idx for idx, item in enumerate(self.class_list)}
        self.num_cats = len(self.class_list)
        self.train_ordered_labels = [self.label2Int[item] for _, item in self.data_list]

    def __getitem__(self, index):
        fn, class_name = self.data_list[index]
        label = self.label2Int[class_name]
        img_path = os.path.join(self.data_root, "images", fn)
        img = self.loader(img_path)
        if self.transform is not None:
            img = self.transform(img)
        return index, img, label

    def __len__(self):
        return len(self.data_list)

    # def shuffle(self):
    #     self.data_list, self.train_ordered_labels = shuffle(self.data_list, self.train_ordered_labels)

# class BaseDataSetTest(unittest.TestCase):
#     def setUp(self) -> None:
#         pass
#     def tearDown(self):
#         pass
#
#     def forward(self):
#         pass


if __name__ == '__main__':
    # unittest.main()
    from tqdm import tqdm
    from torch.utils.data import DataLoader
    from torchvision import transforms
    from engine.configs.parser import BaseOptions
    opts = BaseOptions().opts

    Transform = transforms.Compose([
        transforms.ToTensor()
    ])

    dataset = BaseDataSet(opts, transform=Transform)

    train_loader = DataLoader(dataset, batch_size=8, shuffle=True, num_workers=0) #4

    for episode_idx, (indices, data, targets) in enumerate(tqdm(train_loader)):
        # print(indices)
        # print(data.size())
        # print(targets.size())
        pass
    pass
