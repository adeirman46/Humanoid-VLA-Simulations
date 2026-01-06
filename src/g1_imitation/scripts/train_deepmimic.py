#!/usr/bin/env python3

"""
DeepMimic-style PPO training for LAFAN imitation learning
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
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from lafan_env import G1ImitationEnv


def make_env(rank, motion_name=None):
    """Factory for creating environments"""
    def _init():
        env = G1ImitationEnv(motion_name=motion_name, render_mode=None)
        env = Monitor(env)
        return env
    return _init


def train_deepmimic(
    motion_name=None,
    num_envs: int = 8,
    total_timesteps: int = 5_000_000,
    save_dir: str = None,
):
    """
    Train imitation policy using DeepMimic approach
    
    Args:
        motion_name: Specific motion to train (None = all motions)
        num_envs: Number of parallel environments
        total_timesteps: Total training timesteps
        save_dir: Checkpoint directory
    """
    
    print("\n" + "="*80)
    print("DeepMimic Training - LAFAN Imitation Learning")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        motion_str = motion_name if motion_name else "all_motions"
        save_dir = f"checkpoints/deepmimic_{motion_str}_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create environments
    print(f"Creating {num_envs} environments...")
    if motion_name:
        print(f"  Training on specific motion: {motion_name}")
    else:
        print(f"  Training on all LAFAN motions (random sampling)")
    
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i, motion_name) for i in range(num_envs)])
        eval_env = SubprocVecEnv([make_env(num_envs, motion_name)])
    else:
        env = DummyVecEnv([make_env(0, motion_name)])
        eval_env = DummyVecEnv([make_env(1, motion_name)])
    
    print(f"✓ Created {num_envs} environments\n")
    
    print("Training configuration:")
    print(f"  Timesteps: {total_timesteps:,}")
    print(f"  Environments: {num_envs}")
    print(f"  Learning rate: 3e-4")
    print(f"  Gamma: 0.99 (DeepMimic standard)")
    print(f"  Network: [512, 512] (larger for imitation)")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(50000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='deepmimic',
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
    
    # PPO model - DeepMimic configuration
    print("Creating PPO model (DeepMimic config)...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,  # DeepMimic uses 0.99
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,  # No entropy for imitation
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, 'tensorboard'),
        device='auto',
        policy_kwargs=dict(
            net_arch=[512, 512],  # Larger network for imitation
            activation_fn=torch.nn.Tanh,
        ),
    )
    
    print("✓ Model created\n")
    print(f"Device: {model.device}\n")
    
    print("="*80)
    print("Starting DeepMimic training...")
    print("Robot will learn to imitate LAFAN human motions")
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
    print(f"TensorBoard: tensorboard --logdir {os.path.join(save_dir, 'tensorboard')}\n")
    
    env.close()
    eval_env.close()
    
    return model


def test_policy(model_path: str, motion_name=None, num_episodes: int = 3):
    """Test trained imitation policy"""
    print("\n" + "="*80)
    print("Testing DeepMimic Policy")
    print("="*80 + "\n")
    
    print(f"Loading: {model_path}.zip")
    model = PPO.load(model_path)
    
    env = G1ImitationEnv(motion_name=motion_name, render_mode='human')
    
    print(f"\nRunning {num_episodes} episodes...")
    if motion_name:
        print(f"Motion: {motion_name}\n")
    else:
        print("Random motions\n")
    
    for episode in range(num_episodes):
        obs, info = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False
        
        print(f"Episode {episode+1}:", end=" ", flush=True)
        
        while not done and steps < 1000:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            episode_reward += reward
            steps += 1
            env.render()
        
        print(f"reward={episode_reward:.2f}, steps={steps}, frame={info['frame']}")
    
    env.close()
    print("\n✓ Testing complete!\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='DeepMimic training for LAFAN imitation')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'])
    parser.add_argument('--motion', type=str, default=None,
                        help='Specific motion name (or None for all)')
    parser.add_argument('--num-envs', type=int, default=8)
    parser.add_argument('--timesteps', type=int, default=5_000_000)
    parser.add_argument('--model', type=str, default=None,
                        help='Model path for testing')
    parser.add_argument('--save-dir', type=str, default=None)
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        train_deepmimic(
            motion_name=args.motion,
            num_envs=args.num_envs,
            total_timesteps=args.timesteps,
            save_dir=args.save_dir,
        )
    
    elif args.mode == 'test':
        if args.model is None:
            print("Error: --model required for testing")
            print("Example: --model checkpoints/deepmimic_*/final_model")
            sys.exit(1)
        
        test_policy(args.model, motion_name=args.motion)


if __name__ == '__main__':
    main()
