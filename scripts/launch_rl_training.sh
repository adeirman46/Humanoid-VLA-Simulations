#!/bin/bash

# Launch script for RL training with Stable-Baselines3 PPO
# Trains the Unitree G1 robot using vectorized environments

set -e

echo "========================================="
echo "  G1 Reinforcement Learning Training"
echo "  Using Stable-Baselines3 + PPO"
echo "========================================="
echo ""

# Get workspace directory
WORKSPACE_DIR="$(cd "$(dirname "$0")" && pwd)"

# Activate micromamba environment
echo "🔄 Activating ros2_env environment..."
eval "$(micromamba shell hook --shell bash)"
micromamba activate ros2_env

# Check dependencies
echo "Checking dependencies..."

if ! python3 -c "import stable_baselines3" 2>/dev/null; then
    echo "❌ Error: Stable-Baselines3 not installed"
    echo "Installing dependencies..."
    pip install "stable-baselines3[extra]" sb3-contrib tensorboard
fi

echo "✓ All dependencies installed"
echo ""

# Parse command line arguments
MODE="train"
NUM_ENVS=16
TIMESTEPS=10000000
MODEL=""
SAVE_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --test)
            MODE="test"
            shift
            ;;
        --num-envs)
            NUM_ENVS="$2"
            shift 2
            ;;
        --timesteps)
            TIMESTEPS="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --save-dir)
            SAVE_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--test] [--num-envs NUM] [--timesteps NUM] [--model PATH] [--save-dir DIR]"
            exit 1
            ;;
    esac
done

echo "Configuration:"
echo "  Mode: $MODE"
if [ "$MODE" = "train" ]; then
    echo "  Parallel environments: $NUM_ENVS"
    echo "  Training timesteps: $TIMESTEPS"
    if [ -n "$SAVE_DIR" ]; then
        echo "  Save directory: $SAVE_DIR"
    fi
else
    echo "  Model: $MODEL"
fi
echo ""

# Run training or testing
if [ "$MODE" = "train" ]; then
    echo "🚀 Starting PPO training with Stable-Baselines3..."
    echo "Training progress will be shown below."
    echo ""
    
    CMD="python3 $WORKSPACE_DIR/src/g1_rl/scripts/train_ppo.py --mode train --num-envs $NUM_ENVS --timesteps $TIMESTEPS"
    
    if [ -n "$SAVE_DIR" ]; then
        CMD="$CMD --save-dir $SAVE_DIR"
    fi
    
    eval "$CMD"
else
    if [ -z "$MODEL" ]; then
        echo "❌ Error: --model required for test mode"
        echo "Example: --model src/g1_rl/checkpoints/sb3_ppo_g1_20231228_120000/final_model"
        exit 1
    fi
    
    echo "🧪 Testing trained policy..."
    python3 "$WORKSPACE_DIR/src/g1_rl/scripts/train_ppo.py" \
        --mode test \
        --model "$MODEL"
fi

echo ""
echo "========================================="
echo "  Done!"
echo "========================================="
