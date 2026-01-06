#!/usr/bin/env python3

"""
DeepMimic training WITH live MuJoCo visualization
Watch the robot learn human motions in real-time!
"""

import gymnasium as gym
import numpy as np
import os
import sys
from datetime import datetime
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, BaseCallback
from stable_baselines3.common.monitor import Monitor
import torch
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from lafan_env import G1ImitationEnv


def make_env(rank, motion_name=None, render=False):
    """Factory for creating environments"""
    def _init():
        env = G1ImitationEnv(motion_name=motion_name, render_mode='human' if render else None)
        env = Monitor(env)
        return env
    return _init


class RenderCallback(BaseCallback):
    """
    Callback to render current policy in MuJoCo viewer
    Updates every N steps to show learning progress
    """
    
    def __init__(self, render_freq=100, verbose=0):
        super().__init__(verbose)
        self.render_freq = render_freq
        self.render_env = None
        self.last_obs = None
        
    def _on_training_start(self):
        """Create render environment"""
        print("\n🎬 Opening MuJoCo viewer...")
        self.render_env = G1ImitationEnv(render_mode='human')
        self.last_obs, _ = self.render_env.reset()
        print("✓ Viewer ready - watch the robot learn!\n")
        
    def _on_step(self):
        """Update render environment every N steps"""
        if self.n_calls % self.render_freq == 0:
            # Get action from current policy
            action, _ = self.model.predict(self.last_obs, deterministic=False)
            
            # Step render environment
            self.last_obs, reward, terminated, truncated, info = self.render_env.step(action)
            
            # Render
            self.render_env.render()
            
            # Reset if done
            if terminated or truncated:
                self.last_obs, _ = self.render_env.reset()
        
        return True
    
    def _on_training_end(self):
        """Clean up"""
        if self.render_env:
            self.render_env.close()


def train_with_visualization(
    motion_name=None,
    num_envs: int = 8,
    total_timesteps: int = 5_000_000,
    render_freq: int = 100,
    save_dir: str = None,
):
    """
    Train with LIVE MuJoCo visualization
    """
    
    print("\n" + "="*80)
    print("DeepMimic Training WITH Live Visualization")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        motion_str = motion_name if motion_name else "all_motions"
        save_dir = f"checkpoints/deepmimic_viz_{motion_str}_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create training environments (NO rendering)
    print(f"Creating {num_envs} training environments...")
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i, motion_name, render=False) for i in range(num_envs)])
        eval_env = SubprocVecEnv([make_env(num_envs, motion_name, render=False)])
    else:
        env = DummyVecEnv([make_env(0, motion_name, render=False)])
        eval_env = DummyVecEnv([make_env(1, motion_name, render=False)])
    
    print(f"✓ Created {num_envs} environments\n")
    
    print("Configuration:")
    print(f"  Timesteps: {total_timesteps:,}")
    print(f"  Environments: {num_envs}")
    print(f"  Render every: {render_freq} steps")
    print(f"  Motions: {'All LAFAN' if not motion_name else motion_name}")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(50000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='deepmimic_viz',
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
    
    # RENDER CALLBACK - Shows robot in MuJoCo!
    render_callback = RenderCallback(render_freq=render_freq)
    
    # PPO model
    print("Creating PPO model...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.0,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, 'tensorboard'),
        device='auto',
        policy_kwargs=dict(
            net_arch=[512, 512],
            activation_fn=torch.nn.Tanh,
        ),
    )
    
    print("✓ Model created\n")
    print(f"Device: {model.device}\n")
    
    print("="*80)
    print("Starting training - MuJoCo window will open!")
    print("Watch the robot learn to imitate human motions")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback, render_callback],
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
    print(f"\nFinal model: {final_path}.zip\n")
    
    env.close()
    eval_env.close()
    
    return model


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='DeepMimic training with live visualization')
    parser.add_argument('--motion', type=str, default=None,
                        help='Specific motion name (or None for all)')
    parser.add_argument('--num-envs', type=int, default=8,
                        help='Number of parallel training environments')
    parser.add_argument('--timesteps', type=int, default=5_000_000,
                        help='Total training timesteps')
    parser.add_argument('--render-freq', type=int, default=100,
                        help='Update MuJoCo viewer every N steps')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='Checkpoint directory')
    
    args = parser.parse_args()
    
    train_with_visualization(
        motion_name=args.motion,
        num_envs=args.num_envs,
        total_timesteps=args.timesteps,
        render_freq=args.render_freq,
        save_dir=args.save_dir,
    )
