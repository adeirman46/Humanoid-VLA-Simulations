# Humanoid VLA Simulations

Reinforcement learning and imitation learning for Unitree G1 humanoid robot using MuJoCo and ROS2.

## Quick Start

### 1. LAFAN Imitation Learning (Recommended)

Train the robot to walk using real human motion capture data:

```bash
# Start training + live monitoring
./scripts/run_lafan_training_dual.sh
```

This opens 2 terminals:
- **Terminal 1**: PPO training (8 parallel environments)
- **Terminal 2**: Live MuJoCo visualization

**Based on proven implementation**: [DRLoco](https://github.com/rgalljamov/DRLoco)

### 2. MuJoCo WASD Control

Control the robot with keyboard in MuJoCo:

```bash
./scripts/launch_mujoco_wasd.sh
```

**Controls:**
- `W/S`: Forward/Backward
- `A/D`: Turn Left/Right
- `Space`: Stand still
- `ESC`: Quit

### 3. RL Training (Custom Locomotion)

Train custom walking policies with PPO:

```bash
./scripts/launch_rl_training.sh
```

## Project Structure

```
Humanoid-VLA-Simulations/
├── src/
│   ├── g1_imitation/          # LAFAN imitation learning
│   │   ├── scripts/
│   │   │   ├── train_proven.py    # DRLoco-based training
│   │   │   ├── monitor_training.py # Live visualization
│   │   │   ├── lafan_env.py       # Imitation environment
│   │   │   └── process_lafan.py   # Dataset processing
│   │   ├── data/
│   │   │   ├── lafan1_retargeted/ # Raw LAFAN data
│   │   │   └── processed/         # Processed numpy arrays
│   │   └── checkpoints/           # Trained models
│   │
│   ├── g1_rl/                 # Custom RL training
│   │   └── scripts/
│   │       ├── train_ppo.py
│   │       └── mujoco_rl_env.py
│   │
│   └── g1_controller/         # ROS2 control & WASD
│       └── scripts/
│           └── wasd_controller.py
│
├── scripts/                   # Launch scripts
│   ├── run_lafan_training_dual.sh
│   ├── launch_mujoco_wasd.sh
│   └── launch_rl_training.sh
│
└── README.md
```

## Installation

### Prerequisites

```bash
# MuJoCo
sudo apt install libglfw3 libglew-dev

# Micromamba environment
micromamba create -n ros2_env python=3.11
micromamba activate ros2_env

# Python packages
pip install mujoco gymnasium stable-baselines3 numpy pandas torch
```

### LAFAN Dataset Setup

```bash
cd src/g1_imitation

# Download LAFAN1 retargeted data (requires HuggingFace token)
python3 scripts/download_lafan.py

# Process data
python3 scripts/process_lafan.py
```

**Note**: Add your HuggingFace token to `huggingface.env`:
```bash
echo "YOUR_TOKEN_HERE" > huggingface.env
```

## Training Details

### LAFAN Imitation Learning

**Architecture** (from DRLoco proven implementation):
- Network: `[1024, 512]` with Tanh activation
- Algorithm: PPO with reward scaling (0.1x)
- Learning rate: 5e-4
- Batch size: 256
- n_steps: 4096

**Dataset**: 40 real human motion sequences
- 16 walking variations
- 4 running sequences
- 8 dance moves
- 12 other skills (jumps, fight, etc.)

**Training Command**:
```bash
cd src/g1_imitation
python3 scripts/train_proven.py --motion walk1_subject1 --num-envs 8 --timesteps 5000000
```

**Test Trained Model**:
```bash
python3 scripts/train_proven.py --mode test --model checkpoints/proven_*/final_model
```

### Custom RL Training

**Environment**: Custom MuJoCo environment for G1
- Observation: Joint positions, velocities, body orientation
- Action: Target joint positions (29 DOF)
- Reward: Forward velocity + stability + energy efficiency

**Training**:
```bash
cd src/g1_rl
python3 scripts/train_ppo.py --timesteps 10000000
```

## Available Scripts

### Imitation Learning
- `run_lafan_training_dual.sh` - Training + live monitoring (2 terminals)
- `train_single_motion.sh` - Train on specific motion interactively
- `check_lafan_training.sh` - Check training status

### MuJoCo Control
- `launch_mujoco_wasd.sh` - WASD keyboard control
- `launch_mujoco_fixed_base.sh` - Fixed base testing

### RL Training
- `launch_rl_training.sh` - Start PPO training

### ROS2 (Legacy)
- `launch_g1.sh` - Spawn robot in Gazebo
- `launch_gazebo_house.sh` - Spawn in house world
- `launch_robot_gui.sh` - Joint control GUI

## Monitoring Training

**TensorBoard**:
```bash
tensorboard --logdir src/g1_imitation/checkpoints/
```

**Live Monitoring** (already included in dual script):
```bash
cd src/g1_imitation
python3 scripts/monitor_training.py --checkpoint-dir checkpoints --motion walk1_subject1
```

## Troubleshooting

### Robot falls/flies during training
- ✅ Fixed: Robot now spawns at origin (0, 0, 0.75)
- ✅ Only joint angles copied from reference, not pelvis position

### Training not improving
- ✅ Using proven DRLoco implementation
- ✅ Reward scaling (0.1x) applied
- ✅ Proper hyperparameters from working code

### MuJoCo viewer not opening
```bash
# Check OpenGL
glxinfo | grep "OpenGL version"

# Install if missing
sudo apt install mesa-utils
```

## Research & Implementation

**Based on**:
- [DeepMimic (2018)](https://xbpeng.github.io/projects/DeepMimic/index.html) - Original imitation learning framework
- [DRLoco](https://github.com/rgalljamov/DRLoco) - Working implementation with SB3
- [LocoMuJoCo](https://github.com/robfiras/loco-mujoco) - Imitation learning benchmark

**LAFAN1 Dataset**:
- Source: [HuggingFace](https://huggingface.co/datasets/lvhaidong/LAFAN1_Retargeting_Dataset)
- 40 sequences retargeted for Unitree G1
- Format: CSV (pelvis pose + 29 joint angles)

## Hardware Requirements

- **CPU**: 4+ cores recommended (8 parallel environments)
- **RAM**: 8GB minimum, 16GB recommended
- **GPU**: Optional (PyTorch auto-detects)
- **Storage**: ~500MB for LAFAN dataset

## License

See individual package licenses in `src/*/package.xml`

## Contributing

1. Keep imitation learning code in `src/g1_imitation/`
2. Keep custom RL in `src/g1_rl/`
3. Don't modify `src/g1_controller/` (ROS2 control)
4. Add new launch scripts to `scripts/`

## Citation

If using this code, please cite:
- DeepMimic paper
- DRLoco implementation
- LAFAN1 dataset

---

**Quick Start**: `./scripts/run_lafan_training_dual.sh` for imitation learning with live visualization! 🤖
