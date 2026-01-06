#!/usr/bin/env python3

"""
Stable-Baselines3 PPO Training - OPTIMIZED for Soldier-Like Walking
Hyperparameters tuned for stable torso and coordinated gait
"""

import gymnasium as gym
import numpy as np
import os
import sys
from datetime import datetime
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../g1_controller/scripts'))

from mujoco_rl_env import G1MuJoCoEnv


def make_env(rank, task='walk', render=False):
    """Factory function to create environment"""
    def _init():
        env = G1MuJoCoEnv(task=task, render_mode='human' if render else None)
        env = Monitor(env)
        return env
    return _init


def train_ppo(
    num_envs: int = 16,
    total_timesteps: int = 10_000_000,
    save_dir: str = None,
):
    """Train G1 with OPTIMIZED hyperparameters for soldier-like walking"""
    
    print("\n" + "="*80)
    print("PPO Training - OPTIMIZED for Soldier-Like Walking")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/soldier_walk_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create environments
    print(f"Creating {num_envs} parallel environments...")
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i, task='walk', render=False) for i in range(num_envs)])
        # Use same type for eval to avoid warning
        eval_env = SubprocVecEnv([make_env(num_envs, task='walk', render=False)])
    else:
        env = DummyVecEnv([make_env(0, task='walk', render=False)])
        eval_env = DummyVecEnv([make_env(1, task='walk', render=False)])
    
    print(f"✓ Created {num_envs} environments\n")
    
    print("OPTIMIZED Hyperparameters:")
    print(f"  Total timesteps: {total_timesteps:,}")
    print(f"  Environments: {num_envs}")
    print(f"  Learning rate: 3e-4 (conservative for stability)")
    print(f"  Gamma: 0.998 (long-term focus)")
    print(f"  Steps per env: 8192 (extensive exploration)")
    print(f"  Batch size: 256 (large, stable updates)")
    print(f"  Epochs: 30 (thorough learning)")
    print(f"  Entropy: 0.01 (focused policy)")
    print(f"  Clip range: 0.15 (tight for stability)")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(100000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='soldier_walk',
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_dir,
        log_path=save_dir,
        eval_freq=max(20000 // num_envs, 1),
        deterministic=True,
        render=False,
        n_eval_episodes=10,
    )
    
    # PPO model with OPTIMIZED hyperparameters
    print("Creating PPO model with optimized hyperparameters...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=3e-4,        # Conservative for stability
        n_steps=8192,              # Extensive exploration
        batch_size=256,            # Large batches for stability
        n_epochs=30,               # Thorough learning per update
        gamma=0.998,               # Long-term reward focus
        gae_lambda=0.98,           # Better credit assignment
        clip_range=0.15,           # Tighter clipping for stability
        ent_coef=0.01,             # Focused policy (not too random)
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, 'tensorboard'),
        device='auto',
        policy_kwargs=dict(
            net_arch=[256, 256, 128],  # Larger network
            activation_fn=torch.nn.Tanh,
        ),
    )
    
    print("✓ Model created\n")
    print(f"Device: {model.device}\n")
    
    print("="*80)
    print("Starting training for soldier-like walking...")
    print("Expected: Stable torso, coordinated arm-leg swing, rhythmic gait")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    
    # Save final
    final_path = os.path.join(save_dir, 'final_model')
    model.save(final_path)
    
    print("\n" + "="*80)
    print("Training Complete!")
    print("="*80)
    print(f"\nFinal model: {final_path}.zip")
    print(f"TensorBoard: tensorboard --logdir {os.path.join(save_dir, 'tensorboard')}\n")
    
    env.close()
    eval_env.close()
    
    return model


def test_trained_policy(model_path: str, num_episodes: int = 5, render: bool = True):
    """Test a trained policy"""
    print("\n" + "="*80)
    print("Testing Trained Soldier Walk Policy")
    print("="*80 + "\n")
    
    print(f"Loading: {model_path}.zip")
    model = PPO.load(model_path)
    
    render_mode = 'human' if render else None
    env = G1MuJoCoEnv(task='walk', render_mode=render_mode)
    
    print(f"\nRunning {num_episodes} episodes...")
    if render:
        print("Watch for: stable torso, coordinated limbs, marching gait\n")
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False
        
        while not done and steps < 1000:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            steps += 1
            
            if render:
                env.render()
        
        print(f"Episode {episode+1}: reward={episode_reward:.2f}, steps={steps}")
    
    env.close()
    print("\nTesting complete!\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train soldier-like walking')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'])
    parser.add_argument('--num-envs', type=int, default=16)
    parser.add_argument('--timesteps', type=int, default=10_000_000)
    parser.add_argument('--model', type=str, default=None)
    parser.add_argument('--save-dir', type=str, default=None)
    parser.add_argument('--no-render', action='store_true')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        model = train_ppo(
            num_envs=args.num_envs,
            total_timesteps=args.timesteps,
            save_dir=args.save_dir,
        )
    
    elif args.mode == 'test':
        if args.model is None:
            print("Error: --model required for testing")
            print("Example: --model checkpoints/soldier_walk_*/final_model")
            sys.exit(1)
        
        test_trained_policy(args.model, render=not args.no_render)
