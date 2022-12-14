"""
Normalising simulated point clouds and corresponding meshes.
"""

from pathlib import Path
import multiprocessing
import os
import glob
import logging

import numpy as np
import laspy
import trimesh
import hydra
from omegaconf import DictConfig
from tqdm import tqdm


def apply_transform(mesh, translation, scale_trafo):
    """
    Apply transform.
    """
    mesh.apply_transform(translation)
    mesh.apply_transform(scale_trafo)
    return mesh


def get_transform(mesh):
    """
    Get transform.
    """
    bounds = mesh.extents
    if bounds.min() == 0.0:
        return

    # translate to origin
    translation = (mesh.bounds[0] + mesh.bounds[1]) * 0.5
    translation = trimesh.transformations.translation_matrix(direction=-translation)

    # scale to unit cube
    scale = 1.0 / bounds.max()
    scale_trafo = trimesh.transformations.scale_matrix(factor=scale)

    return translation, scale_trafo


def normalise(kwargs):
    """
    Single-run normalisation.
    kwargs: (filename_base, las)
    """
    # load point cloud and mesh
    index, filename_base, las, scale = kwargs['index'], Path(kwargs['filename']), kwargs['las'], kwargs['scale']
    filename_mesh = (filename_base.parent.parent / 'mesh_normalised' / filename_base.stem).with_suffix('.obj')
    filename_pts = (filename_base.parent.parent / 'cloud_normalised' / filename_base.stem).with_suffix('.npy')

    pts = las.hitObjectId == index
    if not np.any(pts):
        print(f'missing {filename_base}')

    pts = trimesh.PointCloud(las.xyz[pts])
    pts_scale_trafo = trimesh.transformations.scale_matrix(factor=1 / scale)
    pts.apply_transform(pts_scale_trafo)
    mesh = trimesh.load(filename_base)

    # normalise
    translation, scale_trafo = get_transform(mesh)
    mesh = apply_transform(mesh, translation, scale_trafo)  # as-is normalised
    pts = apply_transform(pts, translation, scale_trafo)

    # save data
    mesh.export(filename_mesh)
    np.save(str(filename_pts), pts.vertices)


@hydra.main(config_path='./conf', config_name='config', version_base='1.2')
def normalise_multirun(cfg: DictConfig):
    """
    Normalise point clouds and corresponding meshes.
    """
    # listing by glob.glob() is with arbitrary order and is OS-specific
    filenames = glob.glob(f'{os.path.join(cfg.input_dir, "*" + cfg.object_suffix)}')

    with laspy.open(cfg.cloud_filename) as fh:
        logging.info(f'Points from Header: {fh.header.point_count}')
        las = fh.read()
        logging.info(f'Points from data: {len(las.points)}')

        kwargs_list = []
        for i, filename in enumerate(filenames):
            kwargs_list.append({'index': i, 'filename': filename, 'las': las, 'scale': cfg.scale})

        logging.info('Processing...')
        with multiprocessing.Pool(processes=cfg.threads if cfg.threads else multiprocessing.cpu_count()) as pool:
            # call with multiprocessing
            for _ in tqdm(pool.map(normalise, kwargs_list), total=len(kwargs_list)):
                pass


if __name__ == '__main__':
    normalise_multirun()
