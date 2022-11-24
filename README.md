# Helios++ simulation

Python caller and personal configurations of *[Helios++](https://www.geog.uni-heidelberg.de/gis/helios.html)* for point cloud simulation on urban buildings.

## Prerequisite
* Download one of the *Helios++* [binaries](https://github.com/3dgeo-heidelberg/helios/releases) and extract it to the `./bin` directory. Change `import pyhelios` to `from bin import pyhelios` in `./bin/pyhelios/simulation_build.py` if applicable.
* Create an environment with dependencies with `conda env create --file conda-environment.yml`, or update an existing environment with `conda env update --file conda-environment.yml --prune`.

## Usage
* `python simulate_helios.py`: run simulation with Helios++ CLI.
* `python simulate_pyhelios.py`: run simulation with Helios++ Python binding.
* `python normalise.py`: apply normalisation to point clouds and corresponding meshes (optional).
