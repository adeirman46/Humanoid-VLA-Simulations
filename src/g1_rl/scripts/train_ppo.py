#!/usr/bin/env python3

"""
Stable-Baselines3 PPO Training for Unitree G1
Uses the existing Gymnasium environment with vectorized training
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
from stable_baselines3.common.env_util import make_vec_env

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../g1_controller/scripts'))

# Import existing environment
from mujoco_rl_env import G1MuJoCoEnv


def train_ppo(
    num_envs: int = 16,
    total_timesteps: int = 10_000_000,
    save_dir: str = None,
    learning_rate: float = 3e-4,
    n_steps: int = 2048,
    batch_size: int = 64,
    n_epochs: int = 10,
):
    """
    Train G1 robot using PPO from Stable-Baselines3
    
    Args:
        num_envs: Number of parallel environments
        total_timesteps: Total training timesteps
        save_dir: Directory to save checkpoints
        learning_rate: Learning rate
        n_steps: Number of steps per environment per update
        batch_size: Minibatch size
        n_epochs: Number of epochs per update
    """
    
    print("\n" + "="*80)
    print("PPO Training for Unitree G1 (Stable-Baselines3)")
    print("="*80 + "\n")
    
    # Setup save directory
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/sb3_ppo_g1_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints will be saved to: {save_dir}\n")
    
    # Create vectorized environments
    print(f"Creating {num_envs} parallel environments...")
    
    def make_env(rank, task='walk'):
        """Factory function to create environment"""
        def _init():
            env = G1MuJoCoEnv(task=task, render_mode=None)
            env = Monitor(env)
            return env
        return _init
    
    # Create parallel environments (use SubprocVecEnv for better performance)
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i) for i in range(num_envs)])
    else:
        env = DummyVecEnv([make_env(0)])
    
    print(f"✓ Created {num_envs} environments\n")
    
    # Create evaluation environment
    eval_env = DummyVecEnv([make_env(0, task='walk')])
    
    # Training configuration
    print("Training configuration:")
    print(f"  Total timesteps: {total_timesteps:,}")
    print(f"  Parallel environments: {num_envs}")
    print(f"  Learning rate: {learning_rate}")
    print(f"  Steps per env: {n_steps}")
    print(f"  Batch size: {batch_size}")
    print(f"  Epochs per update: {n_epochs}")
    print("")
    
    # Create callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(50000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='g1_ppo',
        save_replay_buffer=False,
        save_vecnormalize=True,
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_dir,
        log_path=save_dir,
        eval_freq=max(10000 // num_envs, 1),
        deterministic=True,
        render=False,
        n_eval_episodes=5,
    )
    
    # Create PPO model
    print("Creating PPO model...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=learning_rate,
        n_steps=n_steps,
        batch_size=batch_size,
        n_epochs=n_epochs,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, 'tensorboard'),
        device='auto',  # Use GPU if available
    )
    
    print("✓ Model created\n")
    print(f"Using device: {model.device}\n")
    
    # Train
    print("Starting training...")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    
    # Save final model
    final_path = os.path.join(save_dir, 'final_model')
    model.save(final_path)
    
    print("\n" + "="*80)
    print("Training Complete!")
    print("="*80)
    print(f"\nFinal model saved to: {final_path}.zip")
    print(f"Tensorboard logs: {os.path.join(save_dir, 'tensorboard')}")
    print(f"\nTo visualize training:")
    print(f"  tensorboard --logdir {os.path.join(save_dir, 'tensorboard')}")
    print("")
    
    env.close()
    eval_env.close()
    
    return model


def test_trained_policy(model_path: str, num_episodes: int = 5, render: bool = True):
    """
    Test a trained policy
    
    Args:
        model_path: Path to saved model (without .zip extension)
        num_episodes: Number of episodes to run
        render: Whether to render visualization
    """
    print("\n" + "="*80)
    print("Testing Trained Policy")
    print("="*80 + "\n")
    
    # Load model
    print(f"Loading model: {model_path}.zip")
    model = PPO.load(model_path)
    
    # Create environment
    render_mode = 'human' if render else None
    env = G1MuJoCoEnv(task='walk', render_mode=render_mode)
    
    print(f"\nRunning {num_episodes} episodes...")
    if render:
        print("(Watch the MuJoCo viewer window)\n")
    else:
        print("")
    
    for episode in range(num_episodes):
        obs,info = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False
        
        while not done and steps < 1000:
            # Get action from policy
            action, _states = model.predict(obs, deterministic=True)
            
            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            steps += 1
            
            # Render
            if render:
                env.render()
        
        print(f"Episode {episode+1}: reward={episode_reward:.2f}, steps={steps}")
    
    env.close()
    print("\nTesting complete!\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train G1 robot with PPO (SB3)')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'],
                        help='Mode: train or test')
    parser.add_argument('--num-envs', type=int, default=16,
                        help='Number of parallel environments')
    parser.add_argument('--timesteps', type=int, default=10_000_000,
                        help='Total training timesteps')
    parser.add_argument('--model', type=str, default=None,
                        help='Model path for testing (without .zip)')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='Directory to save checkpoints')
    parser.add_argument('--no-render', action='store_true',
                        help='Disable rendering during testing')
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        # Train model
        model = train_ppo(
            num_envs=args.num_envs,
            total_timesteps=args.timesteps,
            save_dir=args.save_dir,
        )
    
    elif args.mode == 'test':
        # Test model
        if args.model is None:
            print("Error: --model required for testing mode")
            print("Example: --model checkpoints/sb3_ppo_g1_20231228_120000/final_model")
            sys.exit(1)
        
        test_trained_policy(args.model, render=not args.no_render)
