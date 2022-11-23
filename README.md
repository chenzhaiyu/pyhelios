# Helios++ simulation

Python caller and personal configurations of *[Helios++](https://www.geog.uni-heidelberg.de/gis/helios.html)* for point cloud simulation on urban buildings.

## Prerequisite
* Download one of the *Helios++* [binaries](https://github.com/3dgeo-heidelberg/helios/releases) and extract it to the `./bin` directory. Change `import pyhelios` to `from bin import pyhelios` in `./bin/pyhelios/simulation_build.py` if applicable.
* Install dependencies with `pip install -r requirements.txt`.

## Usage
* `python simulate.py`: run simulation on the scene specified in `conf/config.yaml`.
* `python normalise.py`: apply normalisation to point clouds and corresponding meshes (optional).