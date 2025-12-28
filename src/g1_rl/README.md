# G1 Reinforcement Learning with MJX

This package provides GPU-accelerated reinforcement learning for the Unitree G1 humanoid robot using:
- **MJX (MuJoCo XLA)**: JAX-based physics simulation for massive parallelization
- **Brax**: Google's RL library optimized for hardware accelerators
- **PPO**: Proximal Policy Optimization algorithm

## Features

- 🚀 **GPU Acceleration**: Train with thousands of parallel environments
- 🤖 **Unitree G1 Robot**: Full 29-DOF humanoid simulation
- 📊 **PPO Training**: State-of-the-art policy optimization
- 💾 **Checkpointing**: Automatic model saving during training
- 🧪 **Easy Testing**: Simple scripts to test trained policies

## Installation

All dependencies should already be installed. If not, run:

```bash
pip install jax jaxlib mujoco-mjx brax optax flax gymnasium
```

## Quick Start

### 1. Test the Environment

First, verify everything is working:

```bash
cd src/g1_rl/scripts
python3 test_mjx_env.py
```

### 2. Start Training

From the workspace root:

```bash
# Basic training (2048 parallel environments)
./launch_rl_training.sh

# Custom configuration
./launch_rl_training.sh --num-envs 4096 --num-timesteps 100000000
```

### 3. Monitor Progress

Training checkpoints are saved in `src/g1_rl/checkpoints/ppo_g1_<timestamp>/`

Each checkpoint includes:
- Model parameters
- Training metrics
- Evaluation scores

### 4. Test Trained Policy

```bash
./launch_rl_training.sh --test --checkpoint src/g1_rl/checkpoints/ppo_g1_<timestamp>/final_model.pkl
```

## Training Details

### Environment

- **Observation Space** (obs_dim=68):
  - Joint positions (29)
  - Joint velocities (29)
  - Base orientation quaternion (4)
  - Base velocity XY (2)
  - Base height (1)
  - Projected gravity (3)

- **Action Space** (act_dim=29):
  - Target joint positions for all 29 actuators

### Reward Function

The reward encourages the robot to:
1. Maintain standing height (0.75m)
2. Walk forward (positive x-velocity)
3. Stay upright (quaternion w ≈ 1)
4. Minimize excessive joint velocities

### PPO Hyperparameters

- Parallel environments: 2048 (adjustable)
- Episode length: 1000 steps
- Learning rate: 3e-4
- Discount factor: 0.99
- Minibatches: 32
- Updates per batch: 4

## File Structure

```
g1_rl/
├── envs/
│   └── g1_mjx_env.py       # MJX environment implementation
├── scripts/
│   ├── train_ppo.py        # PPO training script
│   └── test_mjx_env.py     # Environment test script
├── checkpoints/            # Saved models
├── package.xml
├── setup.py
└── README.md
```

## Performance

On a modern GPU/TPU:
- 2048 environments: ~50,000 steps/second
- 4096 environments: ~80,000 steps/second
- CPU only: ~5,000 steps/second

Training to good walking behavior typically takes:
- 20-50 million timesteps
- 1-3 hours on GPU
- 10-30 hours on CPU

## Customization

### Modify Reward Function

Edit `_compute_reward()` in `envs/g1_mjx_env.py`:

```python
def _compute_reward(self, data: mjx.Data, obs: jax.Array) -> jax.Array:
    # Add your custom reward components here
    ...
```

### Adjust Training Parameters

Edit hyperparameters in `scripts/train_ppo.py` or pass command-line args.

### Change Task

Modify the observation space and reward function for different tasks:
- Standing balance
- Walking
- Running
- Turning
- Stair climbing

## Troubleshooting

### Out of Memory

Reduce `--num-envs`:
```bash
./launch_rl_training.sh --num-envs 1024
```

### No GPU Detected

JAX will fall back to CPU. To enable GPU:
```bash
pip install --upgrade "jax[cuda12]"  # For CUDA 12
```

### Slow Training

- Use more parallel environments if you have GPU/TPU
- Reduce episode_length for faster iterations
- Enable XLA compilation (happens automatically)

## References

- [MuJoCo XLA (MJX)](https://mujoco.readthedocs.io/en/stable/mjx.html)
- [Brax](https://github.com/google/brax)
- [JAX](https://github.com/google/jax)
- [PPO Paper](https://arxiv.org/abs/1707.06347)
