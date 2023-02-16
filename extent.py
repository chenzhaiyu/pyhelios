"""
Calculating extent of OBJ files.
"""

import os
import glob

import numpy as np
import trimesh
import hydra
from omegaconf import DictConfig
from tqdm import tqdm


@hydra.main(config_path='./conf', config_name='config', version_base='1.2')
def get_bbox(cfg: DictConfig):
    filenames = glob.glob(f'{os.path.join(cfg.input_dir, "*" + cfg.object_suffix)}')
    global_bbox = np.array([[0, 0, 0], [0, 0, 0]])  # [minX, minY, minZ, maxX, maxY, maxZ]
    for filename in tqdm(filenames):
        mesh = trimesh.load(filename)
        bbox = mesh.bounds
        update_global_bbox(global_bbox, bbox)
    print(f'Global bbox: {global_bbox}')


def update_global_bbox(global_bbox, bbox):
    global_min = np.minimum(bbox[0], global_bbox[0])
    global_max = np.maximum(bbox[1], global_bbox[1])
    global_bbox[0] = global_min
    global_bbox[1] = global_max


if __name__ == '__main__':
    get_bbox()
