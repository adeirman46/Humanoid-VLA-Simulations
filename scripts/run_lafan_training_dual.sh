#!/bin/bash

# Launch LAFAN Training + Monitoring in separate terminals
# This script opens TWO terminals: one for training, one for visualization

echo "==================================================================="
echo "LAFAN1 Imitation Learning - Dual Terminal Launch"
echo "==================================================================="
echo ""
echo "Launching TWO terminals:"
echo "  Terminal 1: Training (8 envs, 5M timesteps)"
echo "  Terminal 2: Live Monitoring (MuJoCo viewer)"
echo ""
echo "==================================================================="
echo ""

# Get current directory
WORKDIR=$(pwd)

# Check which terminal emulator is available
if command -v gnome-terminal &> /dev/null; then
    TERMINAL="gnome-terminal"
elif command -v xterm &> /dev/null; then
    TERMINAL="xterm"
elif command -v konsole &> /dev/null; then
    TERMINAL="konsole"
else
    echo "❌ Error: No terminal emulator found (gnome-terminal, xterm, or konsole)"
    echo "Please install one of these terminal emulators"
    exit 1
fi

echo "Using terminal: $TERMINAL"
echo ""

# Terminal 1: Training
echo "🚀 Launching Training Terminal..."

if [ "$TERMINAL" = "gnome-terminal" ]; then
    gnome-terminal --title="LAFAN Training - WALK" --geometry=120x40 -- bash -c "
        cd '$WORKDIR'
        eval \"\$(micromamba shell hook --shell bash)\"
        micromamba activate ros2_env
        echo '===================================================='
        echo 'LAFAN1 PROVEN Training (DRLoco Implementation)'
        echo '===================================================='
        echo ''
        echo 'Based on: github.com/rgalljamov/DRLoco'
        echo 'Architecture: [1024, 512] with Tanh'
        echo 'Reward scaling: 0.1x'
        echo 'Motion: walk1_subject1'
        echo 'Environments: 8 parallel'
        echo 'Timesteps: 5M (proven to work)'
        echo ''
        echo 'This is a WORKING implementation!'
        echo ''
        echo 'Checkpoints: src/g1_imitation/checkpoints/'
        echo ''
        echo 'Starting PROVEN training...'
        echo ''
        cd src/g1_imitation
        python3 scripts/train_proven.py --motion walk1_subject1 --num-envs 8 --timesteps 5000000
        echo ''
        echo 'Walking training complete! Press Enter to close...'
        read
    " &
else
    $TERMINAL -title "LAFAN Training - WALK" -geometry 120x40 -e bash -c "
        cd '$WORKDIR'
        eval \"\$(micromamba shell hook --shell bash)\"
        micromamba activate ros2_env
        echo '===================================================='
        echo 'LAFAN1 PROVEN Training (DRLoco)'
        echo '===================================================='
        echo ''
        cd src/g1_imitation
        python3 scripts/train_proven.py --motion walk1_subject1 --num-envs 8 --timesteps 5000000
        echo ''
        echo 'Training complete! Press Enter to close...'
        read
    " &
fi

# Wait a bit for training to start
sleep 5

# Terminal 2: Monitoring
echo "📺 Launching Monitoring Terminal..."

if [ "$TERMINAL" = "gnome-terminal" ]; then
    gnome-terminal --title="LAFAN Monitor" --geometry=120x40 -- bash -c "
        cd '$WORKDIR'
        eval \"\$(micromamba shell hook --shell bash)\"
        micromamba activate ros2_env
        echo '===================================================='
        echo 'LAFAN1 Live Monitoring - MuJoCo Viewer'
        echo '===================================================='
        echo ''
        echo 'Monitoring: walk1_subject1 (matching training)'
        echo 'Mode: CONTINUOUS (no waiting)'
        echo ''
        echo 'Waiting for first checkpoint...'
        echo ''
        sleep 10
        cd src/g1_imitation
        python3 scripts/monitor_training.py --checkpoint-dir checkpoints --motion walk1_subject1
        echo ''
        echo 'Monitoring stopped! Press Enter to close...'
        read
    " &
else
    $TERMINAL -title "LAFAN Monitor" -geometry 120x40 -e bash -c "
        cd '$WORKDIR'
        eval \"\$(micromamba shell hook --shell bash)\"
        micromamba activate ros2_env
        echo '===================================================='
        echo 'LAFAN1 Live Monitoring - MuJoCo Viewer'
        echo '===================================================='
        echo ''
        echo 'Monitoring: walk1_subject1'
        echo ''
        sleep 10
        cd src/g1_imitation
        python3 scripts/monitor_training.py --checkpoint-dir checkpoints --motion walk1_subject1
        echo ''
        echo 'Monitoring stopped! Press Enter to close...'
        read
    " &
fi

sleep 2

echo ""
echo "✅ Both terminals launched!"
echo ""
echo "Terminal 1: Training (background)"
echo "Terminal 2: Monitoring with MuJoCo viewer"
echo ""
echo "To stop:"
echo "  Close the terminal windows OR"
echo "  pkill -f train_deepmimic"
echo ""
echo "Monitor progress:"
echo "  tail -f src/g1_imitation/checkpoints/deepmimic_*/tensorboard/PPO_*/events*"
echo ""
echo "==================================================================="
