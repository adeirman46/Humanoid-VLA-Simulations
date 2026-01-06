# G1 Imitation Learning with LAFAN1

Motion capture imitation learning for Unitree G1 using LAFAN1 dataset.

## Overview

This package implements **DeepMimic-style imitation learning** where the G1 robot learns natural human motions from the LAFAN1 motion capture dataset. Unlike the RL approach in `g1_rl`, this uses real human demonstrations as reference trajectories.

## Features

- ✅ Pre-retargeted LAFAN1 data for G1 robot
- ✅ 77 diverse motion sequences (walk, run, dance, jump)
- ✅ DeepMimic reward for natural motion tracking
- ✅ Completely separate from existing g1_rl package

## Installation

### Dependencies

```bash
# Activate environment
micromamba activate ros2_env

# Install additional dependencies
pip install huggingface_hub scipy
```

### Download LAFAN1 Data

```bash
cd src/g1_imitation
python3 scripts/download_lafan.py
```

This downloads the retargeted LAFAN1 dataset (~50MB) to `data/lafan1_retargeted/`.

## Usage

### 1. Process Data

```bash
python3 scripts/process_lafan.py
```

Converts CSV files to numpy arrays for fast loading.

### 2. Visualize Motions

```bash
python3 scripts/visualize_motion.py --motion walk1
```

Plays back LAFAN motion in MuJoCo to verify data.

### 3. Train Imitation Policy

```bash
python3 scripts/train_deepmimic.py --motion walk1 --timesteps 5000000
```

Trains PPO policy to track the reference motion.

### 4. Test Trained Policy

```bash
python3 scripts/train_deepmimic.py --mode test --model checkpoints/deepmimic_*/best_model
```

## Data Format

LAFAN1 retargeted CSV format (37 columns):
- Columns 0-2: Pelvis position (x, y, z)
- Columns 3-6: Pelvis orientation (quaternion w, x, y, z)
- Columns 7-36: 30 joint angles (radians)

## Technical Approach

### DeepMimic Method

1. **Reference Motion**: Load LAFAN motion as reference trajectory
2. **Observation**: Robot state + current reference frame + next reference frame
3. **Reward**: Similarity between robot pose and reference pose
4. **Training**: PPO learns to minimize pose difference

### Reward Components

```python
r_pose = exp(-k * ||q_robot - q_ref||²)      # Joint positions
r_vel = exp(-k * ||v_robot - v_ref||²)       # Joint velocities
r_ee = exp(-k * ||p_ee_robot - p_ee_ref||²)  # End-effectors
r_com = exp(-k * ||com_robot - com_ref||²)   # Center of mass
```

## Available Motions

LAFAN1 includes 77 sequences across 5 subjects:
- Walking (various speeds/styles)
- Running
- Dancing
- Jumping
- Obstacles navigation
- And more!

## Comparison with g1_rl

| Feature | g1_rl | g1_imitation |
|---------|-------|--------------|
| Approach | Reward shaping | Motion imitation |
| Data | None | LAFAN1 mocap |
| Motions | Learn from scratch | Human demonstrations |
| Naturalness | Depends on reward | Very natural |
| Training | 10-20M steps | 5-10M steps |

## Architecture

```
src/g1_imitation/
├── scripts/
│   ├── download_lafan.py       # Download dataset
│   ├── process_lafan.py         # Preprocess data
│   ├── lafan_env.py             # Imitation environment
│   ├── train_deepmimic.py       # Training script
│   └── visualize_motion.py      # Visualization
├── data/
│   ├── lafan1_retargeted/       # CSV files
│   └── processed/               # Numpy arrays
└── checkpoints/                 # Trained models
```

## Citation

If you use this package, please cite:

```bibtex
@misc{lafan1,
  title={LAFAN1: Ubisoft La Forge Animation Dataset},
  author={Ubisoft La Forge},
  year={2022},
  url={https://github.com/ubisoft/ubisoft-laforge-animation-dataset}
}
```

## License

CC BY-NC-ND 4.0 (LAFAN1 dataset license)

Code: MIT
