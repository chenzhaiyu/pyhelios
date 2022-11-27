# Helios++ simulation

Personal configurations of *[Helios++](https://www.geog.uni-heidelberg.de/gis/helios.html)* for point cloud simulation on urban buildings.

## Prerequisite
* Follow the [instruction](./BUILDME.md) to build *Helios++* from source, or download one of the [binaries](https://github.com/3dgeo-heidelberg/helios/releases) and register the executable path in `conf/config.yaml`. Probably Change `import pyhelios` to `from bin import pyhelios` in `./bin/pyhelios/simulation_build.py` if applicable.
* Create an environment with dependencies with `conda env create --file conda-environment.yml`, or update an existing environment with `conda env update --file conda-environment.yml --prune`.

## Usage
* `python simulate_helios.py`: run simulation with Helios++ CLI.
* `python simulate_pyhelios.py`: run simulation with Helios++ Python binding.
* `python normalise.py`: apply normalisation to point clouds and corresponding meshes (optional).
