# MuJoCo Setup for Unitree G1

This directory now includes MuJoCo integration for RL training with the Unitree G1 robot.

## Quick Start

```bash
# Launch MuJoCo simulator with WASD control
./launch_mujoco_wasd.sh
```

## Files Added

- **launch_mujoco_wasd.sh** - Launch script for MuJoCo + WASD control
- **src/g1_controller/scripts/mujoco_g1_simulator.py** - MuJoCo simulator
- **src/g1_controller/scripts/mujoco_wasd_controller.py** - WASD controller
- **src/g1_controller/scripts/mujoco_rl_env.py** - Gymnasium RL environment

## Requirements

All dependencies are already installed in `ros2_env`:
- MuJoCo 3.3.7
- unitree_sdk2_python
- Gymnasium
- pygame

## External Repositories

- `~/unitree_mujoco` - Official Unitree MuJoCo models
- `~/unitree_sdk2_python` - Unitree SDK2 Python bindings

## Usage

### 1. Manual Control (WASD)

```bash
./launch_mujoco_wasd.sh
```

Controls:
- **W** - Walk forward
- **S** - Walk backward
- **A** - Turn left
- **D** - Turn right
- **Space** - Stand pose
- **ESC** - Quit

### 2. RL Training

```python
from g1_controller.mujoco_rl_env import G1MuJoCoEnv

env = G1MuJoCoEnv(task='stand', render_mode='human')
obs, info = env.reset()

# Your RL training loop here
for step in range(1000):
    action = env.action_space.sample()
    obs, reward, done, truncated, info = env.step(action)
    env.render()
    if done or truncated:
        obs, info = env.reset()

env.close()
```

### 3. With Stable-Baselines3

```python
from g1_controller.mujoco_rl_env import G1MuJoCoEnv
from stable_baselines3 import PPO

env = G1MuJoCoEnv(task='stand')
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)
model.save("g1_stand_ppo")
```

## Documentation

See the [walkthrough](file:///home/irman/.gemini/antigravity/brain/b60d8b31-d835-46f6-9b36-1d4560febb9e/walkthrough.md) for complete documentation.

## Comparison: MuJoCo vs Gazebo

### Use MuJoCo for:
- RL training (much faster)
- Policy optimization
- Sim-to-real transfer

### Use Gazebo for:
- Full system testing
- Sensor simulation
- ROS2 integration testing

Both environments share the same robot model and control interfaces, so you can develop in one and validate in the other!
