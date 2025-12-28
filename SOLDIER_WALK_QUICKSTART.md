# Quick Start Guide: Soldier-Like Walking

## 🎯 What Changed

### Environment Improvements
- **Observations**: 68 → **102 dimensions**
  - Added torso orientation (euler angles)
  - Added torso angular velocity
  - Added projected gravity (IMU-like)
  - Added foot contact sensors
  - Added previous actions (for smoothness)

### Reward Function: 2 → **10 Components**

**Old** (weak signal):
```python
forward_reward + height_penalty
```

**NEW** (comprehensive):
1. Forward velocity (3.0x weight)
2. Torso upright (no roll/pitch)
3. No spinning (yaw stability)
4. Minimal angular momentum
5. Gravity sensing
6. Alternating foot contacts (CPG-inspired)
7. Arm-leg coupling (marching coordination)
8. Action smoothness
9. Energy efficiency
10. Height maintenance + alive bonus + lateral stability

### Hyperparameters (Optimized)
- Gamma: 0.995 → **0.998** (long-term stability)
- Learning rate: 5e-4 → **3e-4** (conservative)
- Steps: 4096 → **8192** (more exploration)
- Batch: 128 → **256** (larger updates)
- Epochs: 20 → **30** (thorough learning)
- Clip: 0.2 → **0.15** (tighter for stability)

---

## 🚀 Usage

### Option 1: Train Without Visualization (Fastest)
```bash
python3 src/g1_rl/scripts/train_ppo.py --num-envs 16 --timesteps 10000000
```

### Option 2: Train WITH Visualization (Recommended!)
```bash
python3 src/g1_rl/scripts/train_ppo_with_render.py --num-envs 16 --timesteps 10000000
```

The MuJoCo window updates every 100 steps showing current policy.

### Option 3: Quick Test (100K steps)
```bash
python3 src/g1_rl/scripts/train_ppo_with_render.py --num-envs 16 --timesteps 100000 --render-freq 50
```

---

## 📊 Expected Results

### Timeline
- **0-500K steps**: Learning to stand without falling
- **500K-2M steps**: Torso stabilization emerging
- **2M-5M steps**: Coordinated walking developing
- **5M+ steps**: Smooth soldier-like marching

### Success Criteria
✅ Torso stays upright (< 10° roll/pitch)  
✅ No spinning (minimal yaw rotation)  
✅ Alternating leg pattern visible  
✅ Arms swing opposite to legs  
✅ Walks forward > 0.5 m/s  
✅ Doesn't fall for full 1000 steps  

---

## 🔍 Monitor Training

```bash
tensorboard --logdir checkpoints/soldier_walk_*/tensorboard
```

Watch for:
- `rollout/ep_rew_mean` increasing
- `rollout/ep_len_mean` reaching 1000
- `eval/mean_reward` improving

---

## 🧪 Test Trained Model

```bash
python3 src/g1_rl/scripts/train_ppo.py --mode test --model checkpoints/soldier_walk_*/best_model
```

---

## ⚙️ Advanced Options

### More Environments (Faster Training)
```bash
python3 src/g1_rl/scripts/train_ppo.py --num-envs 32
```

### Longer Training
```bash
python3 src/g1_rl/scripts/train_ppo.py --timesteps 20000000
```

### Custom Save Directory
```bash
python3 src/g1_rl/scripts/train_ppo.py --save-dir my_experiment
```

---

## 📝 Files Changed

- ✅ [mujoco_rl_env.py](file:///home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts/mujoco_rl_env.py) - Complete rewrite
- ✅ [train_ppo.py](file:///home/irman/Humanoid-VLA-Simulations/src/g1_rl/scripts/train_ppo.py) - Optimized hyperparameters
- ✅ [train_ppo_with_render.py](file:///home/irman/Humanoid-VLA-Simulations/src/g1_rl/scripts/train_ppo_with_render.py) - Fixed + optimized

---

## 🎖️ Ready to Train!

Start with visualization to see the robot learn:

```bash
cd /home/irman/Humanoid-VLA-Simulations
python3 src/g1_rl/scripts/train_ppo_with_render.py
```

The robot should achieve soldier-like marching in **3-5M steps** (vs previous 9M+ with no success)! 🚀
