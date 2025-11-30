# Unitree G1 Humanoid Robot - ROS2 Gazebo Simulation

Complete ROS2 Humble setup for the Unitree G1 humanoid robot with Gazebo simulation and WASD keyboard control.

## Features

- 29 DOF humanoid robot with high-quality meshes
- Gazebo physics simulation with ros2_control
- WASD keyboard control for robot movement
- AWS RoboMaker Small House World environment

---

## Prerequisites

- **OS**: Ubuntu 22.04 or 24.04
- **Micromamba** or Conda
- **Gazebo**: Gazebo Classic
- **Terminal emulator**: gnome-terminal, xterm, or konsole

---

## Installation

### 1. Install Micromamba

```bash
# Install micromamba if not already installed
"${SHELL}" <(curl -L micro.mamba.pm/install.sh)

# Restart shell or source your shell config
source ~/.bashrc  # or ~/.zshrc
```

### 2. Create ROS2 Environment

```bash
# Create environment with Python 3.11 and ROS2 Humble
micromamba create -n ros2_env python=3.11 -c conda-forge

# Activate environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Install ROS2 Humble desktop
micromamba install -y ros-humble-desktop -c conda-forge -c robostack-staging
```

### 3. Install ROS2 Dependencies

```bash
# Install required ROS2 packages
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
# Clone the repository
git clone https://github.com/adeirman46/Humanoid-VLA-Simulations.git
cd Humanoid-VLA-Simulations
```

### 5. Build Workspace

> **Note**: The ros2_control and ros2_controllers packages are already included in the `src/` directory.

```bash
# Ensure environment is activated
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Build the workspace (skip packages with missing dependencies)
colcon build --packages-skip admittance_controller tricycle_controller

# Source the workspace
source install/setup.bash
```

> **Note**: Some controller packages (admittance_controller, tricycle_controller) are skipped because they require additional dependencies (kinematics_interface, ackermann_msgs) that aren't needed for the G1 robot.

---

## Running the Simulation

### Quick Start - WASD Control (Recommended)

```bash
# Make sure you're in the workspace directory
cd ~/Humanoid-VLA-Simulations

# Activate ROS2 environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Launch WASD control in separate terminals
bash launch_wasd_separate_terminal.sh
```

This will:
1. Launch Gazebo with the G1 robot (Terminal 1)
2. Automatically spawn controllers after 5 seconds
3. Open a new terminal for WASD keyboard control after 14 seconds

### Keyboard Controls (in Terminal 2)

| Key | Action |
|-----|--------|
| **W** | Walk Forward |
| **S** | Walk Backward |
| **A** | Turn Left (Counterclockwise) |
| **D** | Turn Right (Clockwise) |
| **SPACE** | Return to Stand Pose |
| **ESC** | Quit Controller |

### Stopping the Simulation

Press **Ctrl+C** in Terminal 1 (the Gazebo launch terminal) to stop everything.

---

## Available Launch Scripts

```bash
./launch_g1.sh                      # RViz visualization only
./launch_gazebo_house.sh            # Gazebo with AWS Small House World
./launch_wasd_control.sh            # WASD control (single terminal)
./launch_wasd_separate_terminal.sh  # WASD control (separate terminals) ⭐ Recommended
```

---

## Troubleshooting

### "Package not found" Error

If you see errors like `package 'g1_package' not found`:

```bash
# Rebuild the workspace
cd ~/Humanoid-VLA-Simulations
colcon build --packages-skip admittance_controller tricycle_controller
source install/setup.bash
```

### Controller Not Spawning

If controllers fail to spawn:

```bash
# Check if controller_manager is running
ros2 service list | grep controller_manager

# Try respawning controllers manually
ros2 run controller_manager spawner joint_state_broadcaster
ros2 run controller_manager spawner position_trajectory_controller
```

### Gazebo Crashes on Launch

```bash
# Clean build and rebuild
rm -rf build install log
colcon build --packages-skip admittance_controller tricycle_controller
source install/setup.bash
```

---

## Project Structure

```
Humanoid-VLA-Simulations/
├── src/
│   ├── g1_package/              # Robot URDF and meshes
│   ├── g1_gazebo_sim/           # Gazebo launch files
│   ├── g1_controller/           # WASD controller and configs
│   ├── ros2_control/            # ROS2 control framework
│   └── ros2_controllers/        # ROS2 controller implementations
├── launch_wasd_separate_terminal.sh  # Main launch script
└── README.md
```

---

## Development

### Adding New Behaviors

Edit the WASD controller to add new movement patterns:

```bash
# Controller script location
src/g1_controller/scripts/wasd_controller.py
```

### Modifying Joint Configurations

Edit controller parameters:

```bash
# Controller config
src/g1_controller/config/g1_controllers.yaml
```

### Changing Initial Pose

Edit URDF joint initial values:

```bash
# Robot URDF
src/g1_package/urdf/g1_29dof_ros2_control.urdf
```

---

## Technical Details

- **ROS2 Version**: Humble
- **Control Framework**: ros2_control with Gazebo plugin
- **Controllers**:
  - `joint_state_broadcaster`: Publishes joint states
  - `position_trajectory_controller`: Accepts trajectory commands
- **DOF**: 29 joints (legs, waist, arms)
- **Communication**: ROS2 action interface for trajectory execution

---

## Credits

- **Robot Model**: Unitree G1 29-DOF Humanoid
- **Environment**: AWS RoboMaker Small House World
- **Framework**: ROS2 Humble with ros2_control

---

**Happy Robotics! 🤖**
