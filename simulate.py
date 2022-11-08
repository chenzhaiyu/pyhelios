"""
Simulating point clouds with Helios++.
"""

import glob

import lxml.etree
import lxml.builder

from bin import pyhelios


def simulate():
    # set logging
    pyhelios.loggingDefault()

    # set seed for default random number generator.
    pyhelios.setDefaultRandomnessGeneratorSeed("123")

    # print current helios version
    print(f'helios version: {pyhelios.getVersion()}')

    # create scene XML
    xml_element = lxml.builder.ElementMaker()
    xml_document = xml_element.document
    xml_scene = xml_element.scene
    xml_part = xml_element.part
    xml_filter = xml_element.filter
    xml_param = xml_element.param
    filenames = glob.glob('data/helsinki/model_base/*.obj')
    records = [
        xml_part(xml_filter(xml_param(type="string", key="filepath", value=filename), xml_param(type="string", key="up", value="z"), type="objloader"),
                 xml_filter(xml_param(type="double", key="scale", value="500"), type="scale"),
                 xml_filter(xml_param(type="vec3", key="offset", value="0;0;0"), type="translate"), id=str(i)) for
        i, filename in enumerate(filenames)]

    xml_tree = xml_document(
        xml_scene(id="helsinki_scene", name="HelsinkiScene",
                  *records
                  )
    )

    # write out xml
    header_str = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str = lxml.etree.tostring(xml_tree, pretty_print=True)
    with open('conf/helsinki_scene.xml', 'wb') as f:
        f.write(header_str)
        f.write(xml_str)

    # build simulation parameters
    simBuilder = pyhelios.SimulationBuilder(
        'conf/als_helsinki.xml',
        'bin/assets/',
        'outputs/',
    )

    # --- does not work ---
    # # scale and translate objects
    # s = 100.0  # scale by factor 100
    # t = [0, 0, 20.0]  # translate upwards
    # for i in range(len(filenames)):
    #     simBuilder.addTranslateFilter(t[0], t[1], t[2], str(i))
    #     simBuilder.addScaleFilter(s, str(i))

    simBuilder.setNumThreads(6)
    simBuilder.setLasOutput(True)
    simBuilder.setZipOutput(True)
    simBuilder.setCallbackFrequency(0)  # run without callback
    simBuilder.setFinalOutput(True)  # return output at join
    simBuilder.setExportToFile(True)  # disable export pointcloud to file
    simBuilder.setRebuildScene(False)
    sim = simBuilder.build()

    sim.start()

    if sim.isStarted():
        print('Simulation has started!')

    while sim.isRunning():
        pass

    if sim.isFinished():
        print('Simulation has finished.')

    # acquire simulated data
    output = sim.join()
    # measurements_array, trajectory_array = pyhelios.outputToNumpy(output)

    # may need to modify line 37 in pyhelios\output_handling
    # to generate hitObjectId for separating objects
    # assert len(measurements_array[0]) == 17


if __name__ == '__main__':
    simulate()
