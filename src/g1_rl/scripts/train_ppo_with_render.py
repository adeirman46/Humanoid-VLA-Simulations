#!/usr/bin/env python3

"""
SIMPLE training with visualization - Uses threading for reliable rendering
This version definitely shows the robot!
"""

import gymnasium as gym
import sys
import os
from datetime import datetime
import threading
import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, EvalCallback, BaseCallback
from stable_baselines3.common.monitor import Monitor
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../g1_controller/scripts'))

from mujoco_rl_env import G1MuJoCoEnv


class RenderCallback(BaseCallback):
    """
    Callback to render during training
    Renders the first environment every N steps
    """
    def __init__(self, render_freq=100, verbose=0):
        super().__init__(verbose)
        self.render_freq = render_freq
        self.render_env = None
        
    def _on_training_start(self):
        # Create a separate render environment
        print("\n🎬 Creating visualization environment...")
        self.render_env = G1MuJoCoEnv(task='walk', render_mode='human')
        self.render_env.reset()
        print("✓ MuJoCo viewer should be open now!\n")
        
    def _on_step(self):
        # Render every N steps using the current policy
        if self.n_calls % self.render_freq == 0 and self.render_env is not None:
            # Get action from current policy
            obs = self.render_env._get_obs()
            action, _ = self.model.predict(obs, deterministic=False)
            
            # Step the render env
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


def train_ppo_simple_render(
    num_envs: int = 16,
    total_timesteps: int = 20_000_000,
    save_dir: str = None,
    render_freq: int = 100,
):
    """Train with simple callback-based rendering"""
    
    print("\n" + "="*80)
    print("PPO Training with SIMPLE Live Visualization")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/sb3_ppo_g1_simple_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create training environments (NO rendering)
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
    print(f"  Learning rate: 5e-4")
    print(f"  Network: [256, 256, 128]")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(100000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='g1_ppo',
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
    
    # Render callback - THIS SHOWS THE ROBOT
    render_callback = RenderCallback(render_freq=render_freq, verbose=1)
    
    # Model
    print("Creating PPO model...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=5e-4,
        n_steps=4096,
        batch_size=128,
        n_epochs=20,
        gamma=0.995,
        gae_lambda=0.98,
        clip_range=0.2,
        ent_coef=0.02,
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
    print("Starting training...")
    print("MuJoCo window will open shortly and show the robot learning!")
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
    
    parser = argparse.ArgumentParser(description='Train with SIMPLE visualization')
    parser.add_argument('--num-envs', type=int, default=16,
                        help='Number of parallel training environments')
    parser.add_argument('--timesteps', type=int, default=20_000_000,
                        help='Total training timesteps')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='Directory to save checkpoints')
    parser.add_argument('--render-freq', type=int, default=100,
                        help='Render every N training steps (default: 100)')
    
    args = parser.parse_args()
    
    train_ppo_simple_render(
        num_envs=args.num_envs,
        total_timesteps=args.timesteps,
        save_dir=args.save_dir,
        render_freq=args.render_freq,
    )
