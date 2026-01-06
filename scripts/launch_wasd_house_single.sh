#!/bin/bash

# Unitree G1 with WASD Keyboard Control in House - Single Terminal Launch Script
# This launches everything in one terminal using the Python launch file

set -e  

echo "========================================="
echo "  Unitree G1 - WASD Control in House"
echo "  (Single Terminal Mode)"
echo "========================================="
echo ""

# Check if micromamba is available
if ! command -v micromamba &> /dev/null; then
    echo "❌ Error: micromamba not found"
    exit 1
fi

echo "✓ Found micromamba"

# Get the workspace directory
WORKSPACE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔄 Activating ros2_env environment..."
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

echo "🔄 Sourcing workspace..."
source "$WORKSPACE_DIR/install/setup.bash"

echo ""
echo "========================================="
echo "  Launching G1 in House with WASD"
echo "========================================="
echo ""
echo "Timeline:"
echo "  0s  - Gazebo starts with house world"
echo "  5s  - Robot spawns in house"
echo "  8s  - Joint state broadcaster loads"
echo "  10s - Position controller loads"
echo "  14s - WASD Controller starts"
echo ""
echo "Keyboard Controls:"
echo "  W - Walk Forward"
echo "  S - Walk Backward (Reverse)"
echo "  A - Turn Left (Counterclockwise)"
echo "  D - Turn Right (Clockwise)"
echo "  SPACE - Stand Pose"
echo "  ESC - Quit"
echo ""
echo "Use CTRL+C to stop everything"
echo ""

# Launch everything using the Python launch file
ros2 launch g1_gazebo_sim gazebo_house_wasd.launch.py
