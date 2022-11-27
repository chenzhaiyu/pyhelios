"""
Simulating point clouds with Helios++.
"""

import hydra
from omegaconf import DictConfig

from bin import pyhelios
from simulate_helios import create_scene


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

    # create scene
    create_scene(cfg)

    # build simulation parameters
    sim_builder = pyhelios.SimulationBuilder(
        f'conf/als_{cfg.dataset_name}.xml',
        'bin/assets/',
        'outputs/',
    )

    sim_builder.setNumThreads(cfg.threads)
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
