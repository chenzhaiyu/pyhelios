"""
Normalising simulated point clouds and corresponding meshes.
"""

from pathlib import Path
from multiprocessing import Pool, RawArray, cpu_count
import os
import glob
import logging

import numpy as np
import laspy
import trimesh
import hydra
from omegaconf import DictConfig
from tqdm import tqdm

# create logger
logger = logging.getLogger('Simulate')

# global dict storing variables passed from initializer
var_dict = {}


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


def normalise(args):
    """
    Single-run normalisation with laspy.
    args: (index, filename)
    """
    index, filename = args
    objects = np.frombuffer(var_dict['objects'], dtype=np.int32) == index

    if np.any(objects):
        filename = Path(filename)
        filename_mesh = (filename.parent.parent.parent / 'mesh_normalised' / filename.stem).with_suffix('.obj')
        filename_pts = (filename.parent.parent.parent / 'cloud_normalised' / filename.stem).with_suffix('.npy')
        filename_mesh.parent.mkdir(parents=True, exist_ok=True)
        filename_pts.parent.mkdir(parents=True, exist_ok=True)

        # load data
        pts = trimesh.PointCloud(np.frombuffer(var_dict['points'], dtype=np.float64).reshape((-1, 3))[objects])
        mesh = trimesh.load(filename)

        # normalise
        translation, scale_trafo = get_transform(mesh)
        mesh = apply_transform(mesh, translation, scale_trafo)  # as-is normalised
        pts = apply_transform(pts, translation, scale_trafo)

        # existing data to append points to
        if filename_pts.exists():
            pts_existing = np.load(str(filename_pts))
            np.save(str(filename_pts), np.vstack((pts_existing, pts.vertices)))

        else:
            # save data
            mesh.export(filename_mesh)
            np.save(str(filename_pts), pts.vertices)


@hydra.main(config_path='./conf', config_name='config', version_base='1.2')
def normalise_multirun(cfg: DictConfig):
    """
    Normalise point clouds and corresponding meshes with laspy and multiprocessing.
    """
    # listing by glob.glob() is with arbitrary order and is OS-specific
    filenames = glob.glob(f'{os.path.join(cfg.input_dir, "*" + cfg.object_suffix)}')

    def init_worker(_points, _objects):
        var_dict['points'] = _points
        var_dict['objects'] = _objects

    with laspy.open(cfg.cloud_filename) as input_las:
        num_points = input_las.header.point_count
        logger.info(f'Reading {cfg.cloud_filename}')
        logger.info(f'Points from header: {num_points}')

        num_chunks = num_points // cfg.chunk_size + 1
        for i, chunk in enumerate(input_las.chunk_iterator(cfg.chunk_size)):
            logger.info(f'Processing chunk {i+1}/{num_chunks}')
            # load data from chunk
            points = np.array([chunk.x, chunk.y, chunk.z]).T
            objects = np.array(chunk.hitObjectId)

            # create shared array across processes
            points_raw = RawArray('d', points.size)
            objects_raw = RawArray('i', objects.size)

            # wrap array for easier manipulation
            points_numpy = np.frombuffer(points_raw, dtype=np.float64).reshape(points.shape)
            objects_numpy = np.frombuffer(objects_raw, dtype=np.int32).reshape(objects.shape)

            # copy data to shared array
            np.copyto(points_numpy, points)
            np.copyto(objects_numpy, objects)

            with Pool(processes=cfg.threads if cfg.threads else cpu_count(), initializer=init_worker,
                      initargs=(points_raw, objects_raw)) as pool:
                for _ in tqdm(pool.imap_unordered(normalise, enumerate(filenames)), total=len(filenames)):
                    pass


if __name__ == '__main__':
    normalise_multirun()
