"""
Normalising simulated point clouds and corresponding meshes.
"""

from pathlib import Path
import glob

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


@hydra.main(config_path='./conf', config_name='config', version_base='1.2')
def normalise(cfg: DictConfig):
    """
    Normalise point clouds and corresponding meshes.
    """
    # listing by glob.glob() is with arbitrary order and is OS-specific
    filenames = glob.glob(f'{os.path.join(cfg.input_dir, "*" + cfg.object_suffix)}')

    with laspy.open(cfg.cloud_filename) as fh:
        print('Points from Header:', fh.header.point_count)
        las = fh.read()
        print(las)
        print('Points from data:', len(las.points))

        for i, filename in enumerate(tqdm(filenames)):
            # load point cloud and mesh
            filename_base = Path(filename)
            filename_mesh = (filename_base.parent.parent / 'mesh_normalised' / filename_base.stem).with_suffix('.obj')
            filename_pts = (filename_base.parent.parent / 'cloud_normalised' / filename_base.stem).with_suffix('.npy')

            pts = las.hitObjectId == i
            if not np.any(pts):
                print(f'missing {filename}')

            pts = trimesh.PointCloud(las.xyz[pts])
            pts_scale_trafo = trimesh.transformations.scale_matrix(factor=1 / cfg.scale)
            pts.apply_transform(pts_scale_trafo)
            mesh = trimesh.load(filename_base)

            # normalise
            translation, scale_trafo = get_transform(mesh)
            mesh = apply_transform(mesh, translation, scale_trafo)  # as-is normalised
            pts = apply_transform(pts, translation, scale_trafo)

            # save data
            mesh.export(filename_mesh)
            np.save(str(filename_pts), pts.vertices)


if __name__ == '__main__':
    normalise()
