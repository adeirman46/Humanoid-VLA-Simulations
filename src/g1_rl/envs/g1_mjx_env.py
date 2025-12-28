#!/usr/bin/env python3

"""
MJX Environment for Unitree G1 Robot
Uses JAX for GPU-accelerated parallel simulations
"""

import jax
import jax.numpy as jnp
from jax import random
from mujoco import mjx
import mujoco
import numpy as np
import os
from typing import Tuple, Dict


class G1MJXEnv:
    """MJX-based environment for Unitree G1 with parallel simulation"""
    
    def __init__(self, model_path: str = None, num_envs: int = 1024):
        """
        Initialize MJX environment
        
        Args:
            model_path: Path to MuJoCo XML model
            num_envs: Number of parallel environments for batch training
        """
        # Find model path
        if model_path is None:
            home_dir = os.path.expanduser("~")
            model_path = os.path.join(home_dir, "unitree_mujoco/unitree_robots/g1/scene.xml")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Could not find G1 model at {model_path}")
        
        print(f"Loading MuJoCo model from: {model_path}")
        
        # Load MuJoCo model
        self.mj_model = mujoco.MjModel.from_xml_path(model_path)
        
        # Convert to MJX model for GPU acceleration
        self.model = mjx.put_model(self.mj_model)
        
        # Number of parallel environments
        self.num_envs = num_envs
        
        # Get dimensions
        self.num_motors = self.mj_model.nu
        self.qpos_dim = self.mj_model.nq
        self.qvel_dim = self.mj_model.nv
        
        # Observation and action dimensions
        self.obs_dim = self.num_motors * 2 + 10  # [joint_pos, joint_vel, base_quat, base_vel_xy, base_height]
        self.act_dim = self.num_motors
        
        # Control parameters
        self.kp = 50.0
        self.kd = 1.0
        
        # Episode parameters
        self.max_steps = 1000
        self.dt = self.mj_model.opt.timestep
        
        print(f"MJX Environment initialized:")
        print(f"  Parallel environments: {num_envs}")
        print(f"  Observation dim: {self.obs_dim}")
        print(f"  Action dim: {self.act_dim}")
        print(f"  Control timestep: {self.dt:.4f}s")
        print(f"  JAX devices: {jax.devices()}")
    
    def reset(self, rng: jax.Array) -> Tuple[mjx.Data, Dict]:
        """
        Reset all parallel environments
        
        Args:
            rng: JAX random key
            
        Returns:
            data: Batched MJX data
            info: Dictionary with initial info
        """
        # Create initial data for all environments
        data = mjx.make_data(self.model)
        
        # Batch the data for parallel environments
        data = jax.tree_map(lambda x: jnp.repeat(jnp.expand_dims(x, 0), self.num_envs, axis=0), data)
        
        # Set standing pose
        data = self._set_standing_pose(data, rng)
        
        # Forward kinematics
        data = mjx.forward(self.model, data)
        
        info = {
            'episode_step': jnp.zeros(self.num_envs, dtype=jnp.int32),
        }
        
        return data, info
    
    def _set_standing_pose(self, data: mjx.Data, rng: jax.Array) -> mjx.Data:
        """Set robot to standing pose with small random perturbations"""
        
        # Standing configuration for legs
        standing_pose = jnp.array([
            -0.4, 0.0, 0.0,  # left_hip: pitch, roll, yaw
            0.8,              # left_knee
            -0.4, 0.0,        # left_ankle: pitch, roll
            -0.4, 0.0, 0.0,  # right_hip: pitch, roll, yaw
            0.8,              # right_knee
            -0.4, 0.0,        # right_ankle: pitch, roll
            0.0, 0.0, 0.0,   # waist: yaw, roll, pitch
            0.3, 0.15, 0.0, 0.5, 0.0, 0.0, 0.0,  # left_arm
            0.3, -0.15, 0.0, 0.5, 0.0, 0.0, 0.0,  # right_arm
        ], dtype=jnp.float32)
        
        # Add small random perturbations for exploration
        noise = random.normal(rng, (self.num_envs, self.num_motors)) * 0.05
        
        # Set joint positions (skip floating base - first 7 values)
        qpos = data.qpos.at[:, 7:7+self.num_motors].set(standing_pose + noise)
        
        # Set base height
        qpos = qpos.at[:, 2].set(0.75)  # z position
        
        # Set base orientation to upright (quaternion: w, x, y, z)
        qpos = qpos.at[:, 3].set(1.0)  # w = 1
        qpos = qpos.at[:, 4:7].set(0.0)  # x, y, z = 0
        
        data = data.replace(qpos=qpos)
        
        return data
    
    def step(self, data: mjx.Data, action: jax.Array, info: Dict) -> Tuple[mjx.Data, jax.Array, jax.Array, jax.Array, Dict]:
        """
        Step all parallel environments
        
        Args:
            data: Current MJX data (batched)
            action: Actions for all environments (num_envs, act_dim)
            info: Current info dictionary
            
        Returns:
            data: Next MJX data
            obs: Observations (num_envs, obs_dim)
            reward: Rewards (num_envs,)
            done: Done flags (num_envs,)
            info: Updated info dictionary
        """
        # Clip actions
        action = jnp.clip(action, -3.14, 3.14)
        
        # Apply PD control
        q_actual = data.qpos[:, 7:7+self.num_motors]
        dq_actual = data.qvel[:, 6:6+self.num_motors]
        
        # PD control law
        tau = self.kp * (action - q_actual) + self.kd * (0.0 - dq_actual)
        
        # Set control
        data = data.replace(ctrl=tau)
        
        # Step simulation
        data = mjx.step(self.model, data)
        
        # Get observation
        obs = self._get_obs(data)
        
        # Compute reward
        reward = self._compute_reward(data, obs)
        
        # Check termination
        done = self._check_done(data, info)
        
        # Update step counter
        info['episode_step'] = info['episode_step'] + 1
        
        return data, obs, reward, done, info
    
    def _get_obs(self, data: mjx.Data) -> jax.Array:
        """Extract observation from MJX data"""
        
        # Joint positions and velocities
        joint_pos = data.qpos[:, 7:7+self.num_motors]
        joint_vel = data.qvel[:, 6:6+self.num_motors]
        
        # Base orientation (quaternion)
        base_quat = data.qpos[:, 3:7]
        
        # Base linear velocity (x, y only)
        base_vel_xy = data.qvel[:, :2]
        
        # Base height
        base_height = data.qpos[:, 2:3]
        
        # Concatenate observation
        obs = jnp.concatenate([
            joint_pos,
            joint_vel,
            base_quat,
            base_vel_xy,
            base_height
        ], axis=-1)
        
        return obs
    
    def _compute_reward(self, data: mjx.Data, obs: jax.Array) -> jax.Array:
        """Compute reward for standing/walking task"""
        
        # Extract components
        base_height = data.qpos[:, 2]
        base_vel = data.qvel[:, :3]  # linear velocity
        joint_vel = data.qvel[:, 6:6+self.num_motors]
        
        # Height reward (stand at 0.75m)
        target_height = 0.75
        height_reward = -jnp.abs(base_height - target_height)
        
        # Forward velocity reward (encourage walking)
        forward_reward = base_vel[:, 0]  # x-velocity
        
        # Penalty for high joint velocities (smoothness)
        velocity_penalty = -0.001 * jnp.sum(jnp.square(joint_vel), axis=-1)
        
        # Upright orientation reward
        quat = data.qpos[:, 3:7]  # w, x, y, z
        upright_reward = quat[:, 0]  # w component (1.0 = perfectly upright)
        
        # Total reward
        reward = height_reward + 0.5 * forward_reward + velocity_penalty + 0.3 * upright_reward
        
        return reward
    
    def _check_done(self, data: mjx.Data, info: Dict) -> jax.Array:
        """Check if episode should terminate"""
        
        # Robot fell (base too low)
        base_height = data.qpos[:, 2]
        fell = base_height < 0.3
        
        # Max steps reached
        max_steps = info['episode_step'] >= self.max_steps
        
        done = jnp.logical_or(fell, max_steps)
        
        return done


def test_env():
    """Test the MJX environment"""
    print("\n" + "="*50)
    print("Testing MJX Environment")
    print("="*50 + "\n")
    
    # Create environment with fewer parallel envs for testing
    env = G1MJXEnv(num_envs=4)
    
    # Initialize JAX random key
    rng = random.PRNGKey(0)
    
    # Reset environment
    print("Resetting environment...")
    data, info = env.reset(rng)
    print(f"✓ Reset successful")
    print(f"  Data shape: qpos={data.qpos.shape}, qvel={data.qvel.shape}")
    print(f"  Initial base heights: {data.qpos[:, 2]}")
    
    # Run some steps
    print("\nRunning 100 steps with random actions...")
    total_rewards = jnp.zeros(env.num_envs)
    
    for i in range(100):
        # Random actions
        rng, action_rng = random.split(rng)
        action = random.uniform(action_rng, (env.num_envs, env.act_dim), minval=-0.1, maxval=0.1)
        
        # Step environment
        data, obs, reward, done, info = env.step(data, action, info)
        total_rewards += reward
        
        if i % 20 == 0:
            print(f"  Step {i}: avg_reward={jnp.mean(reward):.4f}, avg_height={jnp.mean(data.qpos[:, 2]):.4f}")
    
    print(f"\n✓ Test complete!")
    print(f"  Average total reward: {jnp.mean(total_rewards):.4f}")
    print("\nMJX environment is working correctly!")


if __name__ == '__main__':
    test_env()
