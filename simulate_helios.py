"""
Simulating point clouds with Helios++.
"""

import os
import glob
import subprocess

import lxml.etree
import lxml.builder
import hydra
from omegaconf import DictConfig


def create_scene(cfg: DictConfig):
    """
    Create scene file.
    """
    # create scene XML
    xml_element = lxml.builder.ElementMaker()
    xml_document = xml_element.document
    xml_scene = xml_element.scene
    xml_part = xml_element.part
    xml_filter = xml_element.filter
    xml_param = xml_element.param
    filenames = glob.glob(f'{os.path.join(cfg.input_dir, "*" + cfg.object_suffix)}')
    records = [
        xml_part(xml_filter(xml_param(type="string", key="filepath", value=filename),
                            xml_param(type="string", key="up", value="z"), type="objloader"),
                 xml_filter(xml_param(type="double", key="scale", value=f"{cfg.scale}"), type="scale"),
                 xml_filter(xml_param(type="vec3", key="offset", value=f"{cfg.offset}"), type="translate"), id=str(i))
        for i, filename in enumerate(filenames)]

    xml_tree = xml_document(
        xml_scene(id=f"{cfg.dataset_name}_scene", name=f"{cfg.dataset_name.capitalize()}Scene",
                  *records
                  )
    )

    # write out xml
    header_str = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str = lxml.etree.tostring(xml_tree, pretty_print=True)
    with open(f'conf/{cfg.dataset_name}_scene.xml', 'wb') as f:
        f.write(header_str)
        f.write(xml_str)


@hydra.main(config_path='./conf', config_name='config', version_base='1.2')
def simulate(cfg: DictConfig):
    """
    Simulate point cloud given scene.
    """

    # create scene
    create_scene(cfg)

    # run simulation
    if cfg.quiet:
        subprocess.run(
            [f'{cfg.executable_path} conf/als_{cfg.dataset_name}.xml --assets ./bin/assets/ --output ./outputs/  '
             f'--seed {cfg.seed} --nthreads {cfg.threads}'], shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.run(
            [f'{cfg.executable_path} conf/als_{cfg.dataset_name}.xml --assets ./bin/assets/ --output ./outputs/  '
             f'--seed {cfg.seed} --nthreads {cfg.threads}'], shell=True)


if __name__ == '__main__':
    simulate()
