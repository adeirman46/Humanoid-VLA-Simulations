#!/bin/bash

# Launch MuJoCo with FIXED BASE for WASD testing
# This allows testing joint control without balance issues

set -e

echo "========================================="
echo "  MuJoCo WASD - FIXED BASE MODE"
echo "========================================="
echo ""
echo "This mode fixes the robot base so you can"
echo "see WASD joint control working clearly!"
echo ""

WORKSPACE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🔄 Activating environment..."
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

echo "✓ Environment active"
echo ""
echo "Starting simulator with FIXED BASE model..."
echo ""

# Launch simulator with fixed base model
python3 "$WORKSPACE_DIR/src/g1_controller/scripts/mujoco_g1_simulator.py" \
    --model ~/unitree_mujoco/unitree_robots/g1/scene_fixed_base.xml &
SIM_PID=$!

sleep 3

echo "🎮 Opening WASD controller..."

# Launch fixed-base WASD controller
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal -- bash -c "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_fixed_base.py; exec bash"
elif command -v xterm &> /dev/null; then
    xterm -e "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_fixed_base.py; exec bash" &
elif command -v konsole &> /dev/null; then
    konsole -e bash -c "cd '$WORKSPACE_DIR' && eval \"\$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_fixed_base.py; exec bash" &
fi

echo ""
echo "========================================="
echo "  System Running (FIXED BASE)"
echo "========================================="
echo "Watch the MuJoCo window - joints should move!"
echo "Press CTRL+C to stop"
echo ""

wait $SIM_PID
