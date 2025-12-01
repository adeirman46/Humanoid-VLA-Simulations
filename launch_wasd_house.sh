#!/bin/bash

# Unitree G1 with WASD Keyboard Control in House - Separate Terminal Launch Script
# This launches Gazebo with house world and WASD controller in a new terminal

set -e  

echo "========================================="
echo "  Unitree G1 - WASD Control in House"
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
echo "  Launching System in 2 Terminals"
echo "========================================="
echo ""
echo "Terminal 1 (this one): Gazebo House + Controllers"
echo "Terminal 2 (new): WASD Keyboard Control"
echo ""
echo "Timeline:"
echo "  0s  - Gazebo starts with house world"
echo "  5s  - Robot spawns in house"
echo "  8s  - Joint state broadcaster loads"
echo "  10s - Position controller loads"
echo "  14s - WASD Controller opens in new terminal"
echo ""
echo "Keyboard Controls (in new terminal):"
echo "  W - Walk Forward"
echo "  S - Walk Backward (Reverse)"
echo "  A - Turn Left (Counterclockwise)"
echo "  D - Turn Right (Clockwise)"
echo "  SPACE - Stand Pose"
echo "  ESC - Quit"
echo ""
echo "Use CTRL+C in THIS terminal to stop everything"
echo ""

# Launch Gazebo with house world, robot, and controllers (this terminal)
# gui_mode:=false prevents the Python launch file from starting WASD controller
ros2 launch g1_gazebo_sim gazebo_house_wasd.launch.py gui_mode:=false &
GAZEBO_PID=$!

# Wait for controllers to initialize (14 seconds total as per Python launch file timing)
echo "⏳ Waiting for system to initialize..."
sleep 14

# Launch WASD controller in a new terminal
echo "🎮 Opening WASD controller in new terminal..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && source install/setup.bash && ros2 run g1_controller wasd_controller.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && source install/setup.bash && ros2 run g1_controller wasd_controller.py; exec bash" &
elif command -v konsole &> /dev/null; then
    konsole -e bash -c "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && source install/setup.bash && ros2 run g1_controller wasd_controller.py; exec bash" &
else
    echo "❌ Error: No compatible terminal emulator found (tried gnome-terminal, xterm, konsole)"
    echo "Please install one of these terminal emulators"
    kill $GAZEBO_PID 2>/dev/null
    exit 1
fi

echo ""
echo "========================================="
echo "  System Running in House World"
echo "========================================="
echo "Monitor this terminal for system messages"
echo "Use the new terminal for WASD keyboard control"
echo "Robot is spawned inside the house"
echo "Press CTRL+C here to stop everything"
echo ""

# Wait for gazebo process
wait $GAZEBO_PID
