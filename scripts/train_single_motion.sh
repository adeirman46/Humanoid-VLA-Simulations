#!/bin/bash

# Quick script to switch training motion for curriculum learning

echo "==================================================================="
echo "LAFAN Curriculum - Switch Training Motion"
echo "==================================================================="
echo ""
echo "Available motions:"
echo ""
echo "WALKING (recommended first):"
echo "  walk1_subject1  (← Current default)"
echo "  walk2_subject1"
echo "  walk3_subject1"
echo ""
echo "RUNNING (after walking):"
echo "  run1_subject2"
echo "  run2_subject1"
echo ""
echo "SPRINT (after running):"
echo "  sprint1_subject2"
echo ""
echo "DANCE (advanced):"
echo "  dance1_subject1"
echo "  dance2_subject1"
echo ""
echo "OTHER:"
echo "  jumps1_subject1"
echo "  fight1_subject2"
echo ""
echo "==================================================================="
echo ""
read -p "Enter motion name (or press Enter for walk1_subject1): " MOTION

if [ -z "$MOTION" ]; then
    MOTION="walk1_subject1"
fi

echo ""
echo "Training on: $MOTION"
echo "Timesteps: 3M"
echo "Environments: 8"
echo ""
read -p "Press Enter to start training..."

# Activate environment and train
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

cd src/g1_imitation
python3 scripts/train_deepmimic.py --motion "$MOTION" --num-envs 8 --timesteps 3000000

echo ""
echo "Training complete!"
echo "Checkpoint saved to: checkpoints/deepmimic_${MOTION}_*/"
