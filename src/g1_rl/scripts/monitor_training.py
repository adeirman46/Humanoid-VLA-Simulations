#!/usr/bin/env python3

"""
Policy Performance Monitor - Shows how CURRENT checkpoint performs
(Not actual training episodes - those run in parallel processes)

For REAL-TIME training view, use: train_ppo_with_render.py --render-freq 50
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
    """Find the latest checkpoint"""
    checkpoints = glob.glob(os.path.join(checkpoint_dir, "**/soldier_walk_*.zip"), recursive=True)
    if not checkpoints:
        checkpoints = glob.glob(os.path.join(checkpoint_dir, "**/g1_ppo_*.zip"), recursive=True)
    if not checkpoints:
        checkpoints = glob.glob(os.path.join(checkpoint_dir, "**/best_model.zip"), recursive=True)
    
    if not checkpoints:
        return None, None
    
    latest = max(checkpoints, key=os.path.getmtime)
    mtime = os.path.getmtime(latest)
    return latest.replace('.zip', ''), mtime


def continuous_monitor(checkpoint_dir, check_interval=30):
    """
    Monitor - continuously shows how LATEST checkpoint performs
    
    NOTE: This shows NEW episodes using current policy, not actual training episodes!
          For real-time training view, use train_ppo_with_render.py
    """
    
    print("\n" + "="*80)
    print("Policy Performance Monitor")
    print("="*80 + "\n")
    print(f"📁 Checkpoint dir: {checkpoint_dir}")
    print(f"🔄 Check for updates every: {check_interval}s")
    print("\n⚠️  NOTE: This shows current policy performance (new episodes)")
    print("   For REAL training episodes, use: train_ppo_with_render.py\n")
    print("Press Ctrl+C to stop\n")
    
    env = G1MuJoCoEnv(task='walk', render_mode='human')
    
    last_checkpoint = None
    last_mtime = None
    model = None
    episode_count = 0
    last_check_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Check for new checkpoint periodically
            if current_time - last_check_time > check_interval:
                last_check_time = current_time
                latest_checkpoint, mtime = find_latest_checkpoint(checkpoint_dir)
                
                if latest_checkpoint is None:
                    if model is None:
                        print("⏳ Waiting for first checkpoint...")
                        time.sleep(5)
                        continue
                
                # Reload if checkpoint updated
                if latest_checkpoint and mtime != last_mtime:
                    print(f"\n🔄 New checkpoint detected: {os.path.basename(latest_checkpoint)}.zip")
                    print(f"   Last modified: {time.ctime(mtime)}")
                    try:
                        model = PPO.load(latest_checkpoint)
                        last_checkpoint = latest_checkpoint
                        last_mtime = mtime
                        print(f"✓ Loaded updated policy\n")
                    except Exception as e:
                        print(f"⚠️  Loading error: {e}")
                        time.sleep(5)
            
            if model is None:
                time.sleep(5)
                continue
            
            # Run episode with current policy
            episode_count += 1
            obs, info = env.reset()
            episode_reward = 0.0
            steps = 0
            done = False
            
            while not done and steps < 1000:
                action, _states = model.predict(obs, deterministic=False)
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                episode_reward += reward
                steps += 1
                env.render()
            
            # Print episode result
            status = "✓ Success" if steps >= 1000 else "⚠ Fell"
            print(f"{status} | Ep {episode_count} | R={episode_reward:.1f} | Steps={steps} | H={info['base_height']:.2f}m")
    
    except KeyboardInterrupt:
        print("\n\n✓ Monitor stopped")
    finally:
        env.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Monitor current policy performance (not real-time training)',
        epilog='For REAL-TIME training view, use: train_ppo_with_render.py --render-freq 50'
    )
    parser.add_argument('--checkpoint-dir', type=str, required=True)
    parser.add_argument('--check-interval', type=int, default=30,
                        help='Check for new checkpoint every N seconds (default: 30)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.checkpoint_dir):
        print(f"Error: Directory not found: {args.checkpoint_dir}")
        sys.exit(1)
    
    continuous_monitor(args.checkpoint_dir, args.check_interval)
