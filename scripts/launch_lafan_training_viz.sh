#!/bin/bash

# Launch LAFAN training with MuJoCo visualization

echo "==================================================================="
echo "LAFAN1 Imitation Learning - Training with Visualization"
echo "==================================================================="
echo ""
echo "This will:"
echo "  - Train on 40 real LAFAN human motions"
echo "  - Show live MuJoCo viewer"
echo "  - Update viewer every 100 steps"
echo ""
echo "Press Ctrl+C to stop training"
echo ""
echo "==================================================================="
echo ""

# Activate environment
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Go to package directory
cd src/g1_imitation

# Run training with visualization
python3 scripts/train_with_viz.py \
    --num-envs 8 \
    --timesteps 5000000 \
    --render-freq 100

echo ""
echo "Training complete!"
