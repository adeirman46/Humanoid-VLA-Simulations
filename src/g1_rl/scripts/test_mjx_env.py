#!/usr/bin/env python3

"""
Quick test script to verify MJX environment is working
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

print("\n" + "="*60)
print("Testing G1 MJX Environment")
print("="*60 + "\n")

try:
    print("1. Testing JAX import...")
    import jax
    import jax.numpy as jnp
    print(f"   ✓ JAX {jax.__version__}")
    print(f"   ✓ Devices: {jax.devices()}")
    
    print("\n2. Testing MuJoCo and MJX import...")
    import mujoco
    from mujoco import mjx
    print(f"   ✓ MuJoCo {mujoco.__version__}")
    
    print("\n3. Testing Brax import...")
    import brax
    print(f"   ✓ Brax {brax.__version__}")
    
    print("\n4. Creating MJX environment...")
    from envs.g1_mjx_env import G1MJXEnv
    
    # Small number of envs for testing
    env = G1MJXEnv(num_envs=4)
    print(f"   ✓ Environment created")
    print(f"   - Parallel environments: {env.num_envs}")
    print(f"   - Observation dim: {env.obs_dim}")
    print(f"   - Action dim: {env.act_dim}")
    
    print("\n5. Testing environment reset...")
    from jax import random
    rng = random.PRNGKey(0)
    data, info = env.reset(rng)
    print(f"   ✓ Reset successful")
    print(f"   - Base heights: {data.qpos[:, 2]}")
    
    print("\n6. Testing environment step...")
    rng, action_rng = random.split(rng)
    action = random.uniform(action_rng, (env.num_envs, env.act_dim), minval=-0.1, maxval=0.1)
    data, obs, reward, done, info = env.step(data, action, info)
    print(f"   ✓ Step successful")
    print(f"   - Observation shape: {obs.shape}")
    print(f"   - Rewards: {reward}")
    
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour MJX environment is ready for training!")
    print("\nNext steps:")
    print("  1. Start training: ./launch_rl_training.sh")
    print("  2. Adjust num_envs for your hardware")
    print("  3. Monitor training progress in checkpoints/")
    print("")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease ensure all dependencies are installed:")
    print("  pip install jax jaxlib mujoco-mjx brax optax flax gymnasium")
    sys.exit(1)
