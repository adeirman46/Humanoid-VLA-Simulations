#!/bin/bash

# Unitree G1 MuJoCo with WASD Keyboard Control - Separate Terminal Launch Script
# This launches MuJoCo simulator in one terminal and WASD controller in a new terminal

set -e  

echo "========================================="
echo "  Unitree G1 - MuJoCo WASD Control"
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

# Check if MuJoCo is installed
if ! python3 -c "import mujoco" 2>/dev/null; then
    echo "❌ Error: MuJoCo not installed in ros2_env"
    echo "Please install: pip3 install mujoco"
    exit 1
fi

# Check if unitree_sdk2py is installed
if ! python3 -c "import unitree_sdk2py" 2>/dev/null; then
    echo "❌ Error: unitree_sdk2py not installed"
    echo "Please install: cd ~/unitree_sdk2_python && pip3 install -e ."
    exit 1
fi

# Check if pynput is installed
if ! python3 -c "import pynput" 2>/dev/null; then
    echo "⚠️  Warning: pynput not installed, installing now..."
    pip3 install pynput
fi

echo "✓ All dependencies installed"

# Check if unitree_mujoco exists
if [ ! -d "$HOME/unitree_mujoco" ]; then
    echo "❌ Error: unitree_mujoco not found at ~/unitree_mujoco"
    echo "Please clone: git clone https://github.com/unitreerobotics/unitree_mujoco.git ~/unitree_mujoco"
    exit 1
fi

echo "✓ Found unitree_mujoco at ~/unitree_mujoco"

echo ""
echo "========================================="
echo "  Launching System in 2 Terminals"
echo "========================================="
echo ""
echo "Terminal 1 (this one): MuJoCo Simulator"
echo "Terminal 2 (new): Improved WASD Controller (v2)"
echo ""
echo "NOTE: Robot will make SUBTLE movements for balance"
echo "For actual walking, use RL training (see RL environment)"
echo ""
echo "Keyboard Controls (in new terminal):"
echo "  W - Lean Forward"
echo "  S - Lean Backward"
echo "  A - Turn Left (waist rotation)"
echo "  D - Turn Right (waist rotation)"
echo "  SPACE - Stand Pose"
echo "  ESC - Quit"
echo ""
echo "Use CTRL+C in THIS terminal to stop everything"
echo ""

# Launch MuJoCo simulator (this terminal)
echo "🚀 Starting MuJoCo simulator with G1 robot..."
python3 "$WORKSPACE_DIR/src/g1_controller/scripts/mujoco_g1_simulator.py" &
MUJOCO_PID=$!

# Wait a bit for simulator to initialize
sleep 3

# Launch improved WASD controller (v2) in a new terminal
echo "🎮 Opening improved WASD controller (v2) in new terminal..."
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_controller_v2.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_controller_v2.py; exec bash" &
elif command -v konsole &> /dev/null; then
    konsole -e bash -c "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_controller_v2.py; exec bash" &
else
    echo "❌ Error: No compatible terminal emulator found (tried gnome-terminal, xterm, konsole)"
    echo "Please install one of these terminal emulators"
    kill $MUJOCO_PID 2>/dev/null
    exit 1
fi

echo ""
echo "========================================="
echo "  System Running"
echo "========================================="
echo "Monitor this terminal for simulator messages"
echo "Use the new terminal for WASD keyboard control"
echo "Press CTRL+C here to stop everything"
echo ""

# Wait for MuJoCo process
wait $MUJOCO_PID
