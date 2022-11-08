"""
Normalising simulated point clouds and corresponding meshes.
"""

from pathlib import Path
import glob

import numpy as np
import laspy
import trimesh
from tqdm import trange

filename_laz = 'outputs/Survey Playback/helsinki_als/2022-11-07_13-27-05/points/leg000_point.laz'
num_objects = 768


def normalise(mesh, translation, scale_trafo):
    mesh.apply_transform(translation)
    mesh.apply_transform(scale_trafo)
    return mesh


def translation_and_scale(mesh):
    """
    Translation and scale to normalise mesh and point cloud.
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


if __name__ == '__main__':

    # warning: listing by glob.glob() is with arbitrary order and is OS-specific
    filenames = glob.glob('data/helsinki/model_base/*.obj')

    with laspy.open(filename_laz) as fh:
        print('Points from Header:', fh.header.point_count)
        las = fh.read()
        print(las)
        print('Points from data:', len(las.points))

        for i in trange(num_objects):
            # load point cloud and mesh
            filename_base = Path(filenames[i])
            filename_mesh = (filename_base.parent.parent / 'model_normalised' / filename_base.stem).with_suffix('.obj')
            filename_pts = (filename_base.parent.parent / 'points_normalised' / filename_base.stem).with_suffix('.ply')

            pts = las.hitObjectId == i
            pts = trimesh.PointCloud(las.xyz[pts])
            mesh = trimesh.load(filename_base)

            # normalise
            translation, scale_trafo = translation_and_scale(mesh)
            mesh = normalise(mesh, translation, scale_trafo)
            pts = normalise(pts, translation, scale_trafo)

            # save data
            mesh.export(filename_mesh)  # ply/obj
            # np.save(filename_pts, pts.vertices)  # npy
            pts.export(filename_pts)
