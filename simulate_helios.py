"""
Simulating point clouds with Helios++.
"""

import logging
import os
import glob
import math
import subprocess

import lxml.etree
import lxml.builder
import hydra
from omegaconf import DictConfig


def create_survey(cfg: DictConfig):
    """
    Create survey file.
    """
    # create survey XML
    logging.info('creating survey XML...')
    xml_element = lxml.builder.ElementMaker()
    xml_document = xml_element.document
    xml_global_platform_settings = xml_element.platformSettings
    xml_global_scanner_settings = xml_element.scannerSettings
    xml_survey = xml_element.survey
    xml_leg = xml_element.leg
    xml_local_platform_settings = xml_element.platformSettings
    xml_local_scanner_settings = xml_element.scannerSettings

    # horizontal back-and-forth strips given bbox
    num_strips = math.ceil((cfg.bbox_max[1] - cfg.bbox_min[1]) / cfg.strip_interval)
    legs = [None] * num_strips * 2

    # populate legs
    for i in range(num_strips):
        xml_local_platform_settings_left = xml_local_platform_settings(x=f"{cfg.bbox_min[0]}",
                                                                       y=f"{cfg.bbox_min[1] + i * cfg.strip_interval}",
                                                                       z=f"{cfg.flight_height}", onGround="false",
                                                                       template="platform1")
        xml_local_platform_settings_right = xml_local_platform_settings(x=f"{cfg.bbox_max[0]}",
                                                                        y=f"{cfg.bbox_min[1] + i * cfg.strip_interval}",
                                                                        z=f"{cfg.flight_height}", onGround="false",
                                                                        template="platform1")
        if i % 2 == 0:
            # left to right
            legs[2 * i] = xml_leg(xml_local_platform_settings_left,
                                  xml_local_scanner_settings(template="scanner1"),
                                  stripId="mission")
            legs[2 * i + 1] = xml_leg(xml_local_platform_settings_right,
                                      xml_local_scanner_settings(template="scanner1", active="false"),
                                      stripId="mission")
        else:
            # right to left
            legs[2 * i] = xml_leg(
                xml_local_platform_settings_right,
                xml_local_scanner_settings(template="scanner1"), stripId="mission")
            legs[2 * i + 1] = xml_leg(
                xml_local_platform_settings_left,
                xml_local_scanner_settings(template="scanner1", active="false"), stripId="mission")

    xml_tree = xml_document(
        xml_global_platform_settings(id="platform1", movePerSec_m=f"{cfg.move_speed}"),
        xml_global_scanner_settings(active="true", id="scanner1", pulseFreq_hz=f"{cfg.pulse_frequency}",
                                    scanAngle_deg=f"{cfg.scan_angle}",
                                    scanFreq_hz=f"{cfg.scan_frequency}",
                                    trajectoryTimeInterval_s=f"{cfg.time_interval}"),
        xml_survey(name=f"{cfg.dataset_name}_als", platform=f"conf/platforms.xml#{cfg.platform}",
                   scanner=f"conf/scanners_als.xml#{cfg.scanner}",
                   scene=f"conf/{cfg.dataset_name}_scene.xml#{cfg.dataset_name}_scene",
                   *legs
                   )
    )

    # write out xml
    header_str = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str = lxml.etree.tostring(xml_tree, pretty_print=True)
    with open(f'conf/als_{cfg.dataset_name}.xml', 'wb') as f:
        f.write(header_str)
        f.write(xml_str)


def create_scene(cfg: DictConfig):
    """
    Create scene file.
    """
    logging.info('creating scene XML...')
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
    # create survey
    if cfg.create_survey:
        create_survey(cfg)

    # create scene
    if cfg.create_scene:
        create_scene(cfg)

    # run simulation
    if cfg.quiet:
        subprocess.run(
            [f'{cfg.helios_executable} conf/als_{cfg.dataset_name}.xml --assets ./bin/assets/ --output ./outputs/  '
             f'--seed {cfg.seed} --nthreads {cfg.threads} --lasOutput --logFileOnly'], shell=True, stdout=subprocess.DEVNULL)
    else:
        subprocess.run(
            [f'{cfg.helios_executable} conf/als_{cfg.dataset_name}.xml --assets ./bin/assets/ --output ./outputs/  '
             f'--seed {cfg.seed} --nthreads {cfg.threads} --lasOutput --logFile'], shell=True)


if __name__ == '__main__':
    simulate()
