#!/usr/bin/env python3

"""
PPO Training with ONE environment rendered for visualization
The other environments train without rendering for speed
"""

import gymnasium as gym
import sys
import os
from datetime import datetime
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv, VecEnv
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


def train_ppo_with_render(
    num_envs: int = 16,
    total_timesteps: int = 10_000_000,
    save_dir: str = None,
    learning_rate: float = 3e-4,
):
    """Train with one rendered environment"""
    
    print("\n" + "="*80)
    print("PPO Training with Visualization")
    print("="*80 + "\n")
    
    if save_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_dir = f"checkpoints/sb3_ppo_g1_render_{timestamp}"
    
    os.makedirs(save_dir, exist_ok=True)
    print(f"Checkpoints: {save_dir}\n")
    
    # Create environments: first one WITH rendering, rest WITHOUT
    print(f"Creating {num_envs} environments (1 with rendering)...")
    
    env_fns = []
    env_fns.append(make_env(0, render=True))  # First env renders
    for i in range(1, num_envs):
        env_fns.append(make_env(i, render=False))  # Rest don't render
    
    env = SubprocVecEnv(env_fns)
    print(f"✓ Created {num_envs} environments (watch environment #0)\n")
    
    # Eval environment (no rendering during eval for speed)
    eval_env = DummyVecEnv([make_env(0, render=False)])
    
    print("Training configuration:")
    print(f"  Total timesteps: {total_timesteps:,}")
    print(f"  Parallel environments: {num_envs}")
    print(f"  Rendered environment: 1 (environment #0)")
    print(f"  Learning rate: {learning_rate}")
    print("")
    
    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=max(50000 // num_envs, 1),
        save_path=save_dir,
        name_prefix='g1_ppo',
    )
    
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=save_dir,
        log_path=save_dir,
        eval_freq=max(10000 // num_envs, 1),
        deterministic=True,
        render=False,
    )
    
    # Create model
    print("Creating PPO model...")
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=learning_rate,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, 'tensorboard'),
        device='auto',
    )
    
    print("✓ Model created\n")
    print("🎬 MuJoCo viewer will open shortly...")
    print("   (It shows environment #0 out of {})".format(num_envs))
    print("")
    print("Starting training...")
    print("="*80 + "\n")
    
    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[checkpoint_callback, eval_callback],
            progress_bar=True,
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted")
    
    # Save
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
    
    parser = argparse.ArgumentParser(description='Train G1 with visualization')
    parser.add_argument('--num-envs', type=int, default=16,
                        help='Number of parallel environments')
    parser.add_argument('--timesteps', type=int, default=10_000_000,
                        help='Total training timesteps')
    parser.add_argument('--save-dir', type=str, default=None,
                        help='Directory to save checkpoints')
    
    args = parser.parse_args()
    
    train_ppo_with_render(
        num_envs=args.num_envs,
        total_timesteps=args.timesteps,
        save_dir=args.save_dir,
    )
