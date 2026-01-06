#!/usr/bin/env python3

"""
Monitor LAFAN training with live MuJoCo visualization
Loads latest checkpoint and shows robot performing learned motions
"""

import gymnasium as gym
import numpy as np  
import os
import sys
import time
import glob
from pathlib import Path
from stable_baselines3 import PPO

sys.path.append(str(Path(__file__).parent))
from lafan_env import G1ImitationEnv


def find_latest_checkpoint(checkpoint_dir="checkpoints"):
    """Find the most recent checkpoint"""
    
    # Look for checkpoint directories
    checkpoint_dirs = glob.glob(os.path.join(checkpoint_dir, "deepmimic_*"))
    
    if not checkpoint_dirs:
        return None
    
    # Get most recent
    latest_dir = max(checkpoint_dirs, key=os.path.getmtime)
    
    # Look for best_model first, then latest checkpoint
    best_model = os.path.join(latest_dir, "best_model.zip")
    if os.path.exists(best_model):
        return best_model
    
    # Find latest numbered checkpoint
    checkpoints = glob.glob(os.path.join(latest_dir, "deepmimic_*_steps.zip"))
    if checkpoints:
        latest_checkpoint = max(checkpoints, key=os.path.getmtime)
        return latest_checkpoint
    
    return None


def monitor_training(checkpoint_dir="checkpoints", motion_name="walk1_subject1"):
    """
    CONTINUOUS monitoring with live MuJoCo visualization
    No waiting - keeps running and updates policy when checkpoint changes
    """
    
    print("\n" + "="*80)
    print("LAFAN Training Monitor - CONTINUOUS Live Visualization")
    print("="*80 + "\n")
    
    print(f"Checkpoint dir: {checkpoint_dir}")
    print(f"Training motion: {motion_name}")
    print("Mode: CONTINUOUS (no waiting)\n")
    
    # Create environment with SPECIFIC motion (match training!)
    env = G1ImitationEnv(motion_name=motion_name, render_mode='human')
    
    current_model_path = None
    model = None
    episode_count = 0
    
    print("🔍 Waiting for first checkpoint...")
    print("Viewer will stay open continuously...\n")
    
    while True:
        try:
            # Find latest checkpoint
            latest_checkpoint = find_latest_checkpoint(checkpoint_dir)
            
            # Load if new checkpoint found
            if latest_checkpoint and latest_checkpoint != current_model_path:
                print(f"\n📦 NEW checkpoint: {os.path.basename(latest_checkpoint)}")
                try:
                    model = PPO.load(latest_checkpoint)
                    current_model_path = latest_checkpoint
                    print(f"✓ Loaded! Showing {motion_name} performance\n")
                except Exception as e:
                    print(f"⚠️  Error loading: {e}")
                    time.sleep(2)
                    continue
            
            # CONTINUOUS episodes (no waiting!)
            if model:
                obs, info = env.reset()
                episode_reward = 0.0
                steps = 0
                done = False
                
                episode_count += 1
                
                while not done and steps < 1000:
                    action, _states = model.predict(obs, deterministic=True)
                    obs, reward, terminated, truncated, info = env.step(action)
                    done = terminated or truncated
                    episode_reward += reward
                    steps += 1
                    env.render()
                
                print(f"Episode {episode_count}: reward={episode_reward:.2f}, steps={steps}, motion={motion_name}")
                
                # Check for new checkpoint every 10 episodes (not every 30s!)
                if episode_count % 10 == 0:
                    time.sleep(0.1)  # Tiny pause to check for new checkpoint
            else:
                # No model yet, wait a bit
                time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n✓ Monitoring stopped")
            break
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            time.sleep(reload_interval)
    
    env.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor LAFAN training - CONTINUOUS')
    parser.add_argument('--checkpoint-dir', type=str, default='checkpoints',
                        help='Directory containing checkpoints')
    parser.add_argument('--motion', type=str, default='walk1_subject1',
                        help='Motion being trained (must match training!)')
    
    args = parser.parse_args()
    
    monitor_training(
        checkpoint_dir=args.checkpoint_dir,
        motion_name=args.motion,
    )
