# Unitree G1 Humanoid Robot - ROS2 Gazebo Simulation

Complete ROS2 Humble setup for the Unitree G1 humanoid robot with Gazebo simulation and WASD keyboard control.

## Features

- 29 DOF humanoid robot with high-quality meshes
- Gazebo physics simulation with ros2_control
- WASD keyboard control for robot movement
- AWS RoboMaker Small House World environment

---

## Prerequisites

- **OS**: Ubuntu 24.04+
- **Micromamba** or Conda
- **Gazebo**: Gazebo Classic

---

## Installation

### 1. Install Micromamba

```bash
# Install micromamba if not already installed
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)
```

### 2. Create ROS2 Environment

```bash
# Create environment with Python 3.11 and ROS2 Humble
micromamba create -n ros2_env python=3.11 -c conda-forge

# Activate environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Install ROS2 Humble core
micromamba install -y ros-humble-desktop -c conda-forge -c robostack-staging
```

### 3. Install ROS2 Dependencies

```bash
micromamba install -y \
  ros-humble-ros2-control \
  ros-humble-ros2-controllers \
  ros-humble-gazebo-ros2-control \
  ros-humble-joint-state-publisher \
  ros-humble-robot-state-publisher \
  ros-humble-xacro \
  ros-humble-rviz2 \
  -c conda-forge -c robostack-staging
```

### 4. Clone Repository

```bash
git clone https://github.com/adeirman46/Humanoid-VLA-Simulations.git
cd Humanoid-VLA-Simulations
```

### 5. Build ROS2 Controllers from Source

**Important:** The controller packages must be built from source.

```bash
cd src

# Clone required repositories
git clone https://github.com/ros-controls/ros2_control.git -b humble
git clone https://github.com/ros-controls/ros2_controllers.git -b humble

# Build controllers
cd ..
colcon build --packages-select controller_manager joint_state_broadcaster joint_trajectory_controller --symlink-install
```

### 6. Build Workspace

```bash
colcon build --symlink-install
source install/setup.bash
```

---

## Running the Simulation

### Launch with WASD Control

```bash
./launch_wasd_separate_terminal.sh
```

This opens:
- **Terminal 1**: Gazebo simulation with controllers
- **Terminal 2**: WASD keyboard control interface

### Keyboard Controls

| Key | Action |
|-----|--------|
| **W** | Walk Forward |
| **S** | Walk Backward |
| **A** | Turn Left |
| **D** | Turn Right |
| **SPACE** | Stand Pose |
| **ESC** | Quit |

---

## Available Launch Scripts

```bash
./launch_g1.sh                      # RViz visualization only
./launch_gazebo_house.sh            # Gazebo with AWS house world
./launch_wasd_control.sh            # Single terminal WASD control
./launch_wasd_separate_terminal.sh  # Separate terminal WASD control (recommended)
```

---

**Happy Robotics! 🤖**
