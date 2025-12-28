#!/usr/bin/env python3

"""
Training with live visualization - OPTIMIZED for Soldier Walking
Uses callback for reliable rendering during training
"""

import gymnasium as gym
import sys
import os
from datetime import datetime
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, BaseCallback
from stable_baselines3.common.monitor import Monitor
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../g1_controller/scripts'))

from mujoco_rl_env import G1MuJoCoEnv


class RenderCallback(BaseCallback):
    """Callback to show robot during training"""
    def __init__(self, render_freq=100, verbose=0):
        super().__init__(verbose)
        self.render_freq = render_freq
        self.render_env = None
        
    def _on_training_start(self):
        print("\n🎬 Opening visualization...")
        self.render_env = G1MuJoCoEnv(task='walk', render_mode='human')
        self.render_env.reset()
        print("✓ MuJoCo viewer open - watch the robot learn!\n")
        
    def _on_step(self):
        if self.n_calls % self.render_freq == 0 and self.render_env is not None:
            obs = self.render_env._get_obs()
            action, _ = self.model.predict(obs, deterministic=False)
            self.render_env.step(action)
            self.render_env.render()
        return True
    
    def _on_training_end(self):
        if self.render_env is not None:
            self.render_env.close()


def make_env(rank, task='walk'):
    """Factory - no rendering in training envs"""
    def _init():
        env = G1MuJoCoEnv(task=task, render_mode=None)
        env = Monitor(env)
        return env
    return _init


def train_with_visualization(
    num_envs: int = 16,
    total_timesteps: int = 10_000_000,
    save_dir: str = None,
    render_freq: int = 100,
):
    """Train with visualization"""
    
    print("\n" + "="*80)
    print("SOLDIER WALK Training with Live Visualization")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/soldier_viz_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create environments
    print(f"Creating {num_envs} training environments...")
    if num_envs > 1:
        env = SubprocVecEnv([make_env(i) for i in range(num_envs)])
    else:
        env = DummyVecEnv([make_env(0)])
    
    print(f"✓ Training envs created\n")
    
    eval_env = DummyVecEnv([make_env(0)])
    
    print("Configuration:")
    print(f"  Timesteps: {total_timesteps:,}")
    print(f"  Environments: {num_envs}")
    print(f"  Render every: {render_freq} steps")
    print(f"  Optimized for: stable torso + coordinated gait")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(100000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='soldier_viz',
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
    
    render_callback = RenderCallback(render_freq=render_freq, verbose=1)
    
    # Model with OPTIMIZED hyperparameters
    print("Creating optimized PPO model...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=3e-4,
        n_steps=8192,
        batch_size=256,
        n_epochs=30,
        gamma=0.998,
        gae_lambda=0.98,
        clip_range=0.15,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, 'tensorboard'),
        device='auto',
        policy_kwargs=dict(
            net_arch=[256, 256, 128],
            activation_fn=torch.nn.Tanh,
        ),
    )
    
    print("✓ Model created\n")
    print("="*80)
    print("Starting training - MuJoCo window will open shortly!")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback, render_callback],
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted")
    
    final_path = os.path.join(save_dir, 'final_model')
    model.save(final_path)
    
    print("\n" + "="*80)
    print("Complete!")
    print("="*80)
    print(f"\nModel: {final_path}.zip\n")
    
    env.close()
    eval_env.close()
    
    return model


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Train with visualization')
    parser.add_argument('--num-envs', type=int, default=16)
    parser.add_argument('--timesteps', type=int, default=10_000_000)
    parser.add_argument('--save-dir', type=str, default=None)
    parser.add_argument('--render-freq', type=int, default=100)
    
    args = parser.parse_args()
    
    train_with_visualization(
        num_envs=args.num_envs,
        total_timesteps=args.timesteps,
        save_dir=args.save_dir,
        render_freq=args.render_freq,
    )
