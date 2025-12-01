# Install script for directory: /home/irman/Humanoid-VLA-Simulations/src/g1_controller

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/home/irman/Humanoid-VLA-Simulations/install/g1_controller")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/home/irman/micromamba/envs/ros2_env/bin/x86_64-conda-linux-gnu-objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/environment" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/pythonpath.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/environment" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/pythonpath.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python3.11/site-packages/g1_controller-0.1.0-py3.11.egg-info" TYPE DIRECTORY FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_python/g1_controller/g1_controller.egg-info/")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/python3.11/site-packages/g1_controller" TYPE DIRECTORY FILES "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/g1_controller/" REGEX "/[^/]*\\.pyc$" EXCLUDE REGEX "/\\_\\_pycache\\_\\_$" EXCLUDE)
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  execute_process(
        COMMAND
        "/home/irman/micromamba/envs/ros2_env/bin/python3" "-m" "compileall"
        "lib/python3.11/site-packages/g1_controller"
      )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/g1_controller" TYPE PROGRAM FILES
    "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/stand_controller.py"
    "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/zero_pose_controller.py"
    "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/gui_controller.py"
    "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/ros2_control_gui.py"
    "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/wasd_controller.py"
    "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/wasd_controller_v2.py"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE DIRECTORY FILES "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/config")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE DIRECTORY FILES "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/launch")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/package_run_dependencies" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_index/share/ament_index/resource_index/package_run_dependencies/g1_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/parent_prefix_path" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_index/share/ament_index/resource_index/parent_prefix_path/g1_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/environment" TYPE FILE FILES "/home/irman/micromamba/envs/ros2_env/share/ament_cmake_core/cmake/environment_hooks/environment/ament_prefix_path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/environment" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/ament_prefix_path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/environment" TYPE FILE FILES "/home/irman/micromamba/envs/ros2_env/share/ament_cmake_core/cmake/environment_hooks/environment/path.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/environment" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/path.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/local_setup.bash")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/local_setup.sh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/local_setup.zsh")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/local_setup.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_environment_hooks/package.dsv")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/ament_index/resource_index/packages" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_index/share/ament_index/resource_index/packages/g1_controller")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller/cmake" TYPE FILE FILES
    "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_core/g1_controllerConfig.cmake"
    "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/ament_cmake_core/g1_controllerConfig-version.cmake"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/g1_controller" TYPE FILE FILES "/home/irman/Humanoid-VLA-Simulations/src/g1_controller/package.xml")
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
if(CMAKE_INSTALL_COMPONENT)
  if(CMAKE_INSTALL_COMPONENT MATCHES "^[a-zA-Z0-9_.+-]+$")
    set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INSTALL_COMPONENT}.txt")
  else()
    string(MD5 CMAKE_INST_COMP_HASH "${CMAKE_INSTALL_COMPONENT}")
    set(CMAKE_INSTALL_MANIFEST "install_manifest_${CMAKE_INST_COMP_HASH}.txt")
    unset(CMAKE_INST_COMP_HASH)
  endif()
else()
  set(CMAKE_INSTALL_MANIFEST "install_manifest.txt")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "/home/irman/Humanoid-VLA-Simulations/build/g1_controller/${CMAKE_INSTALL_MANIFEST}"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
