"""
Simulating point clouds with Helios++.
"""

import os
import glob

import lxml.etree
import lxml.builder
import hydra
from omegaconf import DictConfig

from bin import pyhelios


@hydra.main(config_path='./conf', config_name='config', version_base='1.2')
def simulate(cfg: DictConfig):
    """
    Simulate point cloud given scene.
    """
    # set logging
    pyhelios.loggingDefault()

    # set seed for default random number generator.
    pyhelios.setDefaultRandomnessGeneratorSeed(f"{cfg.seed}")

    # print current helios version
    print(f'helios version: {pyhelios.getVersion()}')

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

    # build simulation parameters
    sim_builder = pyhelios.SimulationBuilder(
        f'conf/als_{cfg.dataset_name}.xml',
        'bin/assets/',
        'outputs/',
    )

    sim_builder.setNumThreads(6)
    sim_builder.setLasOutput(True)
    sim_builder.setZipOutput(True)
    sim_builder.setCallbackFrequency(0)  # run with callback
    sim_builder.setFinalOutput(False)    # return output at join
    sim_builder.setExportToFile(True)    # export point cloud to file
    sim_builder.setRebuildScene(False)
    sim = sim_builder.build()

    sim.start()

    if sim.isStarted():
        print('Simulation has started!')

    while sim.isRunning():
        pass

    if sim.isFinished():
        print('Simulation has finished.')

    # acquire simulated data
    sim.join()


if __name__ == '__main__':
    simulate()
