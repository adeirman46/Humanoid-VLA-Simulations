# Quick Guide: Making WASD Work

## The Problem

**Bipedal balance is extremely hard!** What you're experiencing is normal - free-floating bipedal robots need:
1. Active balance control (ZMP/MPC)
2. RL-trained walking policies  
3. Or a fixed base for testing

## Solutions

### Option 1: Fixed Base Testing (RECOMMENDED FIRST)

I've created a fixed-base mode so you can see WASD actually works:

1. **Copy the model with fixed base:**
```bash
cd ~/unitree_mujoco/unitree_robots/g1
cp scene.xml scene_fixed_base.xml
```

2. **Edit scene_fixed_base.xml** - find the `<freejoint/>` line and comment it out:
```xml
<!-- <freejoint/> -->  <!-- COMMENTED = FIXED BASE -->
```

3. **Run with fixed base:**
```bash
cd ~/Humanoid-VLA-Simulations

# Terminal 1:
python3 src/g1_controller/scripts/mujoco_g1_simulator.py --model ~/unitree_mujoco/unitree_robots/g1/scene_fixed_base.xml

# Terminal 2:
python3 src/g1_controller/scripts/mujoco_wasd_fixed_base.py
```

You'll see the robot move its joints clearly without falling!

### Option 2: Use Unitree's Built-in Examples

The official unitree_mujoco has working controllers:

```bash
cd ~/unitree_mujoco/simulate_python
python3 unitree_mujoco.py  # Starts simulator

# In another terminal:
cd ~/unitree_mujoco/example/python  
python3 stand_go2.py  # Example controller
```

### Option 3: RL Training for Real Walking

For actual bipedal walking, train an RL policy:

```bash
cd ~/Humanoid-VLA-Simulations
python3 src/g1_controller/scripts/mujoco_rl_env.py
```

Then use Stable-Baselines3 PPO to train.

## Why This Happens

- **Simple position control ≠ Balance**: Humanoids constantly adjust to stay upright
- **MuJoCo = Realistic physics**: Unlike some game engines, it doesn't cheat
- **Professional solutions use**:
  - Model Predictive Control (MPC)
  - Zero Moment Point (ZMP) control
  - Deep RL (PPO, SAC)
  - Whole-Body Control frameworks

## Quick Test

Want to see it work RIGHT NOW?

```bash
cd ~/Humanoid-VLA-Simulations
python3 test_balance.py  # Just holds standing pose
```

If this works, the system is fine - you just need proper balance control!
