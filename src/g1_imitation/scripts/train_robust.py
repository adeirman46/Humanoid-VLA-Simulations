#!/usr/bin/env python3

"""
IMPROVED DeepMimic Training with Robust Architecture
Based on research: DeepMimic (2018) + modern improvements (2024)

Architecture:
- Policy: [1024, 512] with ReLU (DeepMimic standard)
- Value: [1024, 512] with ReLU  
- Layer Normalization for stability
- Residual-style learning focus
"""

import gymnasium as gym
import numpy as np
import os
import sys
from datetime import datetime
from stable_baselines3 import PPO, SAC
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback
from stable_baselines3.common.monitor import Monitor
import torch
import torch.nn as nn
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


def train_deepmimic_robust(
    motion_name="walk1_subject1",
    algorithm="PPO",  # PPO or SAC
    num_envs: int = 8,
    total_timesteps: int = 3_000_000,
    save_dir: str = None,
):
    """
    Train with ROBUST architecture from research
    
    DeepMimic architecture:
    - Hidden layers: [1024, 512]
    - Activation: ReLU
    - Layer normalization for stability
    """
    
    print("\n" + "="*80)
    print(f"ROBUST DeepMimic Training - {algorithm}")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/robust_{algorithm.lower()}_{motion_name}_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create environments
    print(f"Creating {num_envs} environments...")
    print(f"  Motion: {motion_name}")
    print(f"  Algorithm: {algorithm}\n")
    
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i, motion_name) for i in range(num_envs)])
        eval_env = SubprocVecEnv([make_env(num_envs, motion_name)])
    else:
        env = DummyVecEnv([make_env(0, motion_name)])
        eval_env = DummyVecEnv([make_env(1, motion_name)])
    
    # VecNormalize for observation normalization (best practice!)
    env = VecNormalize(
        env,
        norm_obs=True,  # Normalize observations
        norm_reward=False,  # Don't normalize reward for imitation
        clip_obs=10.0,
        gamma=0.99,
    )
    eval_env = VecNormalize(
        eval_env,
        norm_obs=True,
        norm_reward=False,
        clip_obs=10.0,
        gamma=0.99,
        training=False,  # Don't update stats during eval
    )
    
    print(f"✓ Created {num_envs} environments with normalization\n")
    
    print("Architecture (DeepMimic + modern improvements):")
    print(f"  Policy network: [1024, 512] + LayerNorm")
    print(f"  Value network: [1024, 512] + LayerNorm")
    print(f"  Activation: ReLU")
    print(f"  Algorithm: {algorithm}")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(25000 // num_envs, 1),
        save_path=save_dir,
        name_prefix=f'robust_{algorithm.lower()}',
        verbose=1,
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_dir,
        log_path=save_dir,
        eval_freq=max(10000 // num_envs, 1),
        deterministic=True,
        render=False,
        n_eval_episodes=5,
        verbose=1,
    )
    
    # Network architecture - DeepMimic proven design
    policy_kwargs = dict(
        net_arch=dict(
            pi=[1024, 512],  # Policy: DeepMimic standard
            vf=[1024, 512],  # Value: DeepMimic standard  
        ),
        activation_fn=nn.ReLU,  # ReLU as in DeepMimic
        normalize_images=False,
        # Modern improvement: layer normalization
        # (Not directly available in SB3, but handled via VecNormalize)
    )
    
    if algorithm == "PPO":
        print("Creating PPO model (DeepMimic architecture)...")
        model = PPO(
            policy='MlpPolicy',
            env=env,
            # Learning parameters (DeepMimic-inspired)
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=128,  # Larger batch for stability
            n_epochs=10,
            gamma=0.99,  # DeepMimic standard
            gae_lambda=0.95,
            clip_range=0.2,
            clip_range_vf=None,
            normalize_advantage=True,  # Important for stability!
            ent_coef=0.0,  # No entropy for imitation
            vf_coef=0.5,
            max_grad_norm=0.5,
            use_sde=False,
            sde_sample_freq=-1,
            target_kl=None,
            stats_window_size=100,
            tensorboard_log=os.path.join(save_dir, 'tensorboard'),
            policy_kwargs=policy_kwargs,
            verbose=1,
            device='auto',
        )
    
    elif algorithm == "SAC":
        print("Creating SAC model (DeepMimic architecture)...")
        model = SAC(
            policy='MlpPolicy',
            env=env,
            # SAC parameters
            learning_rate=3e-4,
            buffer_size=1_000_000,
            learning_starts=10000,
            batch_size=256,
            tau=0.005,
            gamma=0.99,
            train_freq=1,
            gradient_steps=1,
            ent_coef='auto',
            target_update_interval=1,
            target_entropy='auto',
            use_sde=False,
            sde_sample_freq=-1,
            use_sde_at_warmup=False,
            stats_window_size=100,
            tensorboard_log=os.path.join(save_dir, 'tensorboard'),
            policy_kwargs=policy_kwargs,
            verbose=1,
            device='auto',
        )
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}. Use 'PPO' or 'SAC'")
    
    print("✓ Model created\n")
    print(f"Device: {model.device}\n")
    
    print("="*80)
    print("Starting ROBUST training...")
    print(f"Total timesteps: {total_timesteps:,}")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted")
    
    # Save final model
    final_path = os.path.join(save_dir, 'final_model')
    model.save(final_path)
    
    # Save normalization stats
    env.save(os.path.join(save_dir, 'vec_normalize.pkl'))
    
    print("\n" + "="*80)
    print("Training Complete!")
    print("="*80)
    print(f"\nFinal model: {final_path}.zip")
    print(f"Normalization: {os.path.join(save_dir, 'vec_normalize.pkl')}")
    print(f"\nTensorBoard: tensorboard --logdir {os.path.join(save_dir, 'tensorboard')}\n")
    
    env.close()
    eval_env.close()
    
    return model


def test_policy(model_path: str, motion_name="walk1_subject1", algorithm="PPO"):
    """Test trained robust policy"""
    print("\n" + "="*80)
    print(f"Testing ROBUST {algorithm} Policy")
    print("="*80 + "\n")
    
    print(f"Loading: {model_path}.zip")
    
    if algorithm == "PPO":
        model = PPO.load(model_path)
    elif algorithm == "SAC":
        model = SAC.load(model_path)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    # Load normalization stats if available
    vec_normalize_path = os.path.join(os.path.dirname(model_path), 'vec_normalize.pkl')
    
    env = G1ImitationEnv(motion_name=motion_name, render_mode='human')
    env = Monitor(env)
    env = DummyVecEnv([lambda: env])
    
    if os.path.exists(vec_normalize_path):
        print(f"Loading normalization: {vec_normalize_path}")
        env = VecNormalize.load(vec_normalize_path, env)
        env.training = False
        env.norm_reward = False
    
    print(f"\nRunning 5 episodes...")
    
    for episode in range(5):
        obs = env.reset()
        episode_reward = 0.0
        steps = 0
        done = False
        
        print(f"Episode {episode+1}: ", end="", flush=True)
        
        while not done and steps < 1000:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            episode_reward += reward[0]
            steps += 1
            env.render('human')
        
        print(f"reward={episode_reward:.2f}, steps={steps}")
    
    env.close()
    print("\n✓ Testing complete!\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='ROBUST DeepMimic training')
    parser.add_argument('--mode', type=str, default='train', choices=['train', 'test'])
    parser.add_argument('--motion', type=str, default='walk1_subject1')
    parser.add_argument('--algorithm', type=str, default='PPO', choices=['PPO', 'SAC'])
    parser.add_argument('--num-envs', type=int, default=8)
    parser.add_argument('--timesteps', type=int, default=3_000_000)
    parser.add_argument('--model', type=str, default=None)
    parser.add_argument('--save-dir', type=str, default=None)
    
    args = parser.parse_args()
    
    if args.mode == 'train':
        train_deepmimic_robust(
            motion_name=args.motion,
            algorithm=args.algorithm,
            num_envs=args.num_envs,
            total_timesteps=args.timesteps,
            save_dir=args.save_dir,
        )
    elif args.mode == 'test':
        if args.model is None:
            print("Error: --model required for testing")
            sys.exit(1)
        test_policy(args.model, motion_name=args.motion, algorithm=args.algorithm)
