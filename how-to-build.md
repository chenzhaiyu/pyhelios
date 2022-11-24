* Set `BOOST_ROOT` in `cmake/CMakePybinds.cmake`
```cmake
# ---  PYTHON BINDINGS  --- #
# ------------------------- #
if(${PYTHON_BINDING})
    # Set PYTHON_BINDING to compile boost with python binding support
    set(BOOST_ROOT "/workspace/envs/cpp/boost_1_79_0")
    find_package(Boost 1.71.0 REQUIRED COMPONENTS
        ${BASE_BOOST_COMPONENTS} python${PYTHON_VERSION}
    )
    # Add PYTHON_BINDING define to compile binding code
    add_definitions(-DPYTHON_BINDING)
    add_definitions(-DBOOST_PYTHON_STATIC_LIB)
else()
    set(BOOST_ROOT "/workspace/envs/cpp/boost_1_79_0")
    find_package(Boost 1.71.0 REQUIRED COMPONENTS
        ${BASE_BOOST_COMPONENTS}
    )
endif()
if(Boost_FOUND)
    message(STATUS "boost found")
    message("Boost_INCLUDE_DIRS: " ${Boost_INCLUDE_DIRS})
    include_directories(${Boost_INCLUDE_DIRS})
    message("Boost_LIBRARIES: " ${Boost_LIBRARIES})
endif()
```

* Set `GLM_ENABLE_EXPERIMENTAL`

This is to address the following error:
```bash
error: #error "GLM: GLM_GTX_hash is an experimental extension and may change in the future. Use #define GLM_ENABLE_EXPERIMENTAL before including it, if you really want to use it."
```
Add the following line to `CMakeList.txt`:
```cmake
add_definitions(-D GLM_ENABLE_EXPERIMENTAL)
```

* Fix `armadillo` version

This is to address the following error:
```bash
In file included from /workspace/envs/helios/src/platform/InterpolatedMovingPlatform.h:4:0,
                 from /workspace/envs/helios/src/platform/InterpolatedMovingPlatformEgg.h:4,
                 from /workspace/envs/helios/src/assetloading/XmlAssetsLoader.cpp:25:
/workspace/envs/helios/src/platform/trajectory/DesignTrajectoryFunction.h: In constructor 'DesignTrajectoryFunction::DesignTrajectoryFunction(const arma::Col<double>&, const arma::Mat<double>&, const arma::Mat<double>&)':
/workspace/envs/helios/src/platform/trajectory/DesignTrajectoryFunction.h:72:35: error: 'const class arma::subview_row<double>' has no member named 'as_col'; did you mean 'is_col'?
             frontierValues.row(0).as_col(),
                                   ^~~~~~
                                   is_col
In file included from /workspace/envs/helios/src/assetloading/XmlAssetsLoader.cpp:20:0:
/workspace/envs/helios/src/maths/fluxionum/TemporalDesignMatrix.h: In instantiation of 'void fluxionum::TemporalDesignMatrix<TimeType, VarType>::dropRows(const uvec&) [with TimeType = double; VarType = double; arma::uvec = arma::Col<long long unsigned int>]':
/workspace/envs/helios/src/maths/fluxionum/TemporalDesignMatrix.h:406:17:   required from 'std::size_t fluxionum::TemporalDesignMatrix<TimeType, VarType>::slopeFilter(VarType) [with TimeType = double; VarType = double; std::size_t = long unsigned int]'
/workspace/envs/helios/src/assetloading/XmlAssetsLoader.cpp:640:72:   required from here
/workspace/envs/helios/src/maths/fluxionum/TemporalDesignMatrix.h:329:9: error: no matching function for call to 'arma::Col<double>::shed_rows(const uvec&)'
         t.shed_rows(indices);
         ^
```

The [default package](https://packages.ubuntu.com/bionic/libarmadillo-dev) is old. Download the source of a [newer version](https://arma.sourceforge.net/download.html) then install it:
```
tar -xvf armadillo-11.4.2.tar.xz
cd armadillo-11.4.2
./configure 
make 
sudo make install
```

* Fix `ogr_geometry`

This is to address the following error:
```bash
/workspace/envs/helios/src/assetloading/ScenePart.h:13:10: fatal error: ogr_geometry.h: No such file or directory
 #include <ogr_geometry.h>
          ^~~~~~~~~~~~~~~~
compilation terminated.
```

`libgdal-dev` requires `libarmadillo-dev (1:8.400.0+dfsg-2)`, while `libarmadillo-dev (1:8.400.0+dfsg-2)` is not compatibale in Helios++. One needs to build GDAL from source:
```bash
# https://gdal.org/development/dev_environment.html
# https://gdal.org/download.html#current-release (tested with 3.5.1)
cd gdal-3.5.1
mkdir build
cd build
cmake ..
cmake --build .
cmake --build . --target install
```

Note that `lib/armadillo` will be searched with high priority:
```cmake
# cmake/CMakeLibraries.cmake
# Armadillo
if(EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/lib/armadillo)  # Use armadillo from lib
  set(ARMADILLO_INCLUDE_DIRS ${CMAKE_CURRENT_SOURCE_DIR}/lib/armadillo/include)
  if(WIN32)
    set(ARMADILLO_LIBRARIES ${CMAKE_CURRENT_SOURCE_DIR}/lib/armadillo/Release/armadillo.lib)
  else()
    set(ARMADILLO_LIBRARIES ${CMAKE_CURRENT_SOURCE_DIR}/lib/armadillo/libarmadillo.so)
  endif()
else()  # Try to find already installed armadillo
  find_package(Armadillo REQUIRED)
endif()
if(LAPACK_LIB)
  # Add custom lapack library to armadillo if specified
  set(ARMADILLO_LIBRARIES ${ARMADILLO_LIBRARIES} ${LAPACK_LIB})
endif()
include_directories(${ARMADILLO_INCLUDE_DIRS})
message("Armadillo include: " ${ARMADILLO_INCLUDE_DIRS})
message("Armadillo libraries: " ${ARMADILLO_LIBRARIES})
```

* Export `LDFLAGS`

This is to address the linking error:
```bash
[100%] Linking CXX executable helios
/usr/bin/ld: CMakeFiles/helios.dir/src/maths/rigidmotion/RigidMotionR3Factory.cpp.o: undefined reference to symbol 'ddot_'
//usr/lib/x86_64-linux-gnu/libblas.so.3: error adding symbols: DSO missing from command line
collect2: error: ld returned 1 exit status
CMakeFiles/helios.dir/build.make:2491: recipe for target 'helios' failed
```

Execute the following line:
```bash
# https://zhangboyi.gitlab.io/post/2020-09-14-resolve-dso-missing-from-command-line-error/
export LDFLAGS="-Wl,--copy-dt-needed-entries"
```

* Build the project
```bash
cmake .
make -j 8
```

* Test the installation
```bash
(base) root@dadbd301b70b:/workspace/envs/helios# ./helios --test
TEST Randomness generation test                           [PASSED]
TEST Noise sources test                                   [PASSED]
TEST Discrete time test                                   [PASSED]
TEST Voxel parsing test                                   [PASSED]
TEST Ray intersection test                                [PASSED]
TEST Grove test                                           [PASSED]
TEST Serialization test                                   [PASSED]
TEST Asset loading test                                   [PASSED]
TEST Survey copy test                                     [PASSED]
TEST Plane fitter test                                    [PASSED]
TEST LadLut test                                          [PASSED]
TEST Platform physics test                                [PASSED]
TEST Functional platform test                             [PASSED]
TEST Scene part split test                                [PASSED]
TEST Rigid motion test                                    [PASSED]
TEST Fluxionum test                                       [PASSED]
TEST Energy models test                                   [PASSED]
TEST HPC test                                             [PASSED]
```
