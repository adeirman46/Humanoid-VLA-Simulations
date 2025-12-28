#!/usr/bin/env python3

"""
Live monitoring script - visualize latest checkpoint while training continues
Automatically reloads the latest checkpoint every few minutes
"""

import gymnasium as gym
import sys
import os
import time
import glob
from stable_baselines3 import PPO

sys.path.append(os.path.join(os.path.dirname(__file__), '../../g1_controller/scripts'))
from mujoco_rl_env import G1MuJoCoEnv


def find_latest_checkpoint(checkpoint_dir):
    """Find the latest checkpoint in directory"""
    checkpoints = glob.glob(os.path.join(checkpoint_dir, "**/g1_ppo_*.zip"), recursive=True)
    if not checkpoints:
        checkpoints = glob.glob(os.path.join(checkpoint_dir, "**/best_model.zip"), recursive=True)
    
    if not checkpoints:
        return None
    
    # Sort by modification time
    latest = max(checkpoints, key=os.path.getmtime)
    return latest.replace('.zip', '')


def monitor_training(checkpoint_dir, reload_interval=300):
    """
    Monitor training by visualizing latest checkpoint
    
    Args:
        checkpoint_dir: Directory containing checkpoints
        reload_interval: Seconds between reloading checkpoint (default: 5 minutes)
    """
    
    print("\n" + "="*80)
    print("Live Training Monitor")
    print("="*80 + "\n")
    print(f"Watching: {checkpoint_dir}")
    print(f"Reload interval: {reload_interval}s")
    print("\nPress Ctrl+C to stop\n")
    
    # Create environment
    env = G1MuJoCoEnv(task='walk', render_mode='human')
    
    last_checkpoint = None
    model = None
    
    try:
        while True:
            # Find latest checkpoint
            latest_checkpoint = find_latest_checkpoint(checkpoint_dir)
            
            if latest_checkpoint is None:
                print("⏳ Waiting for first checkpoint...")
                time.sleep(10)
                continue
            
            # Reload if new checkpoint found
            if latest_checkpoint != last_checkpoint:
                print(f"\n🔄 Loading: {os.path.basename(latest_checkpoint)}.zip")
                try:
                    model = PPO.load(latest_checkpoint)
                    last_checkpoint = latest_checkpoint
                    print("✓ Model loaded successfully\n")
                except Exception as e:
                    print(f"⚠️  Error loading checkpoint: {e}")
                    time.sleep(10)
                    continue
            
            if model is None:
                time.sleep(10)
                continue
            
            # Run one episode
            print("🎬 Running episode...")
            obs, info = env.reset()
            episode_reward = 0.0
            steps = 0
            done = False
            
            while not done and steps < 1000:
                # Get action from latest policy
                action, _states = model.predict(obs, deterministic=False)
                
                # Step
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                episode_reward += reward
                steps += 1
                
                # Render
                env.render()
            
            print(f"✓ Episode complete: reward={episode_reward:.2f}, steps={steps}")
            print(f"⏰ Waiting {reload_interval}s before next episode...\n")
            
            # Wait before next episode
            time.sleep(reload_interval)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped")
    finally:
        env.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor training with live visualization')
    parser.add_argument('--checkpoint-dir', type=str, required=True,
                        help='Directory containing checkpoints')
    parser.add_argument('--reload-interval', type=int, default=300,
                        help='Seconds between checkpoint reloads (default: 300)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.checkpoint_dir):
        print(f"Error: Directory not found: {args.checkpoint_dir}")
        print("\nExample checkpoint directories:")
        checkpoint_base = "src/g1_rl/checkpoints"
        if os.path.exists(checkpoint_base):
            for d in os.listdir(checkpoint_base):
                print(f"  {os.path.join(checkpoint_base, d)}")
        sys.exit(1)
    
    monitor_training(args.checkpoint_dir, args.reload_interval)
