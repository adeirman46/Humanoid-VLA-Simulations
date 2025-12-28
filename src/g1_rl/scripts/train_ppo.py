#!/usr/bin/env python3

"""
Stable-Baselines3 PPO Training for Unitree G1 - IMPROVED VERSION
Better hyperparameters and reward shaping for walking
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
    total_timesteps: int = 20_000_000,
    save_dir: str = None,
    learning_rate: float = 5e-4,  # Increased for faster learning
    n_steps: int = 4096,  # Increased for better exploration
    batch_size: int = 128,  # Larger batches
    n_epochs: int = 20,  # More epochs per update
):
    """
    Train G1 robot using PPO with IMPROVED hyperparameters
    """
    
    print("\n" + "="*80)
    print("PPO Training for Unitree G1 (IMPROVED - Better Walking)")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/sb3_ppo_g1_improved_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create environments - all same render mode
    print(f"Creating {num_envs} parallel environments...")
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i, task='walk', render=False) for i in range(num_envs)])
    else:
        env = DummyVecEnv([make_env(0, task='walk', render=False)])
    
    print(f"✓ Created {num_envs} environments\n")
    
    # Eval environment
    eval_env = DummyVecEnv([make_env(0, task='walk', render=False)])
    
    print("IMPROVED Training configuration:")
    print(f"  Total timesteps: {total_timesteps:,}")
    print(f"  Parallel environments: {num_envs}")
    print(f"  Learning rate: {learning_rate} (INCREASED)")
    print(f"  Steps per env: {n_steps} (INCREASED)")
    print(f"  Batch size: {batch_size} (LARGER)")
    print(f"  Epochs per update: {n_epochs} (MORE)")
    print(f"  Entropy coefficient: 0.02 (INCREASED for exploration)")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(100000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='g1_ppo_improved',
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
    
    # Create PPO model with IMPROVED hyperparameters
    print("Creating PPO model with improved hyperparameters...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=learning_rate,
        n_steps=n_steps,
        batch_size=batch_size,
        n_epochs=n_epochs,
        gamma=0.995,  # Slightly higher discount for long-term walking
        gae_lambda=0.98,  # Higher GAE for better credit assignment
        clip_range=0.2,
        ent_coef=0.02,  # INCREASED for more exploration
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
    
    print("✓ Model created with improved architecture\n")
    print(f"Using device: {model.device}\n")
    
    print("Starting improved training...")
    print("With better reward shaping, this should learn faster!")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted")
    
    # Save final
    final_path = os.path.join(save_dir, 'final_model')
    model.save(final_path)
    
    print("\n" + "="*80)
    print("Training Complete!")
    print("="*80)
    print(f"\nFinal model: {final_path}.zip")
    print(f"Tensorboard: tensorboard --logdir {os.path.join(save_dir, 'tensorboard')}\n")
    
    env.close()
    eval_env.close()
    
    return model


def test_trained_policy(model_path: str, num_episodes: int = 5, render: bool = True):
    """Test a trained policy"""
    print("\n" + "="*80)
    print("Testing Trained Policy")
    print("="*80 + "\n")
    
    print(f"Loading: {model_path}.zip")
    model = PPO.load(model_path)
    
    render_mode = 'human' if render else None
    env = G1MuJoCoEnv(task='walk', render_mode=render_mode)
    
    print(f"\nRunning {num_episodes} episodes...")
    if render:
        print("(Watch the MuJoCo viewer)\n")
    
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
    import torch
    
    parser = argparse.ArgumentParser(description='Train G1 with IMPROVED PPO')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'],
                        help='Mode: train or test')
    parser.add_argument('--num-envs', type=int, default=16,
                        help='Number of parallel environments')
    parser.add_argument('--timesteps', type=int, default=20_000_000,
                        help='Total training timesteps')
    parser.add_argument('--model', type=str, default=None,
                        help='Model path for testing (without .zip)')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='Directory to save checkpoints')
    parser.add_argument('--no-render', action='store_true',
                        help='Disable rendering during testing')
    
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
            print("Example: --model checkpoints/sb3_ppo_g1_improved_*/final_model")
            sys.exit(1)
        
        test_trained_policy(args.model, render=not args.no_render)
