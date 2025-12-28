#!/usr/bin/env python3

"""
Gymnasium RL Environment for Unitree G1 in MuJoCo
Provides standard RL interface for training
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
import mujoco
import os


class G1MuJoCoEnv(gym.Env):
    """Gymnasium environment for Unitree G1 in MuJoCo"""
    
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 30}
    
    def __init__(self, model_path=None, render_mode=None, task='stand'):
        """
        Initialize the G1 RL environment
        
        Args:
            model_path: Path to G1 MJCF model
            render_mode: 'human' for visualization, 'rgb_array' for headless
            task: Task to perform ('stand', 'walk', 'balance')
        """
        super().__init__()
        
        self.render_mode = render_mode
        self.task = task
        
        # Find model path
        if model_path is None:
            home_dir = os.path.expanduser("~")
            model_path = os.path.join(home_dir, "unitree_mujoco/unitree_robots/g1/scene.xml")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Could not find G1 model at {model_path}"
                )
        
        # Load MuJoCo model
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        
        # Number of actuators
        self.num_motors = self.model.nu
        
        # Define observation space
        # Observation: [joint_pos (29), joint_vel (29), base_orientation (4), base_vel (6)]
        obs_dim = self.num_motors * 2 + 4 + 6  # 68 dimensions
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )
        
        # Define action space (joint position targets)
        self.action_space = spaces.Box(
            low=-3.14, high=3.14, shape=(self.num_motors,), dtype=np.float32
        )
        
        # Control parameters
        self.kp = 50.0
        self.kd = 1.0
        
        # Episode parameters
        self.max_episode_steps = 1000
        self.current_step = 0
        
        # Viewer for rendering
        self.viewer = None
        
        print(f"G1 MuJoCo RL Environment initialized")
        print(f"  Task: {task}")
        print(f"  Observation dim: {obs_dim}")
        print(f"  Action dim: {self.num_motors}")
    
    def _get_obs(self):
        """Get current observation"""
        # Joint positions and velocities (skip floating base)
        qpos_start = 7
        qvel_start = 6
        
        joint_pos = self.data.qpos[qpos_start:qpos_start + self.num_motors]
        joint_vel = self.data.qvel[qvel_start:qvel_start + self.num_motors]
        
        # Base orientation (quaternion)
        base_quat = self.data.qpos[:4]
        
        # Base velocity (linear + angular)
        base_vel = self.data.qvel[:6]
        
        # Concatenate observation
        obs = np.concatenate([
            joint_pos,
            joint_vel,
            base_quat,
            base_vel
        ])
        
        return obs.astype(np.float32)
    
    def _get_info(self):
        """Get additional info"""
        # Base position
        base_pos = self.data.qpos[:3]
        base_height = base_pos[2]
        
        return {
            'base_height': base_height,
            'time': self.data.time
        }
    
    def reset(self, seed=None, options=None):
        """Reset environment to initial state"""
        super().reset(seed=seed)
        
        # Reset MuJoCo simulation
        mujoco.mj_resetData(self.model, self.data)
        
        # Set initial pose (standing)
        self._set_standing_pose()
        
        # Step forward to stabilize
        for _ in range(10):
            mujoco.mj_step(self.model, self.data)
        
        self.current_step = 0
        
        observation = self._get_obs()
        info = self._get_info()
        
        return observation, info
    
    def _set_standing_pose(self):
        """Set robot to standing pose"""
        # Joint indices (skip floating base - 7 qpos values)
        qpos_start = 7
        
        # Simple standing configuration
        # Left leg
        self.data.qpos[qpos_start + 0] = -0.4   # left_hip_pitch
        self.data.qpos[qpos_start + 3] = 0.8    # left_knee
        self.data.qpos[qpos_start + 4] = -0.4   # left_ankle_pitch
        
        # Right leg
        self.data.qpos[qpos_start + 6] = -0.4   # right_hip_pitch
        self.data.qpos[qpos_start + 9] = 0.8    # right_knee
        self.data.qpos[qpos_start + 10] = -0.4  # right_ankle_pitch
        
        # Arms
        self.data.qpos[qpos_start + 15] = 0.3   # left_shoulder_pitch
        self.data.qpos[qpos_start + 16] = 0.15  # left_shoulder_roll
        self.data.qpos[qpos_start + 18] = 0.5   # left_elbow
        
        self.data.qpos[qpos_start + 22] = 0.3   # right_shoulder_pitch
        self.data.qpos[qpos_start + 23] = -0.15 # right_shoulder_roll
        self.data.qpos[qpos_start + 25] = 0.5   # right_elbow
        
        # Set base height
        self.data.qpos[2] = 0.75  # Base z-position (standing height)
    
    def step(self, action):
        """Execute one environment step"""
        # Clip action
        action = np.clip(action, self.action_space.low, self.action_space.high)
        
        # Apply PD control
        qpos_start = 7
        qvel_start = 6
        
        q_actual = self.data.qpos[qpos_start:qpos_start + self.num_motors]
        dq_actual = self.data.qvel[qvel_start:qvel_start + self.num_motors]
        
        # PD control
        position_error = action - q_actual
        velocity_error = 0.0 - dq_actual  # Target velocity is 0
        
        tau = self.kp * position_error + self.kd * velocity_error
        self.data.ctrl[:] = tau
        
        # Step simulation
        mujoco.mj_step(self.model, self.data)
        
        # Get observation
        observation = self._get_obs()
        info = self._get_info()
        
        # Compute reward based on task
        reward = self._compute_reward(observation, info)
        
        # Check termination
        terminated = self._is_terminated(info)
        
        # Check truncation (max steps)
        self.current_step += 1
        truncated = self.current_step >= self.max_episode_steps
        
        return observation, reward, terminated, truncated, info
    
    def _compute_reward(self, obs, info):
        """Compute reward based on task - IMPROVED for better walking"""
        base_height = info['base_height']
        
        if self.task == 'stand':
            # Reward for maintaining upright standing pose
            target_height = 0.75
            height_reward = -abs(base_height - target_height)
            
            # Penalty for high velocities (should stand still)
            joint_vel = obs[self.num_motors:self.num_motors*2]
            velocity_penalty = -0.01 * np.sum(np.square(joint_vel))
            
            reward = height_reward + velocity_penalty
            
        elif self.task == 'walk':
            # IMPROVED WALKING REWARD
            # Get velocities
            joint_pos = obs[:self.num_motors]
            joint_vel = obs[self.num_motors:self.num_motors*2]
            base_quat = obs[self.num_motors*2:self.num_motors*2+4]
            base_vel = obs[-6:]  # Last 6 elements are base velocity
            
            # 1. Forward velocity reward (MAIN OBJECTIVE - increased weight)
            forward_vel = base_vel[0]  # x-velocity
            forward_reward = 2.0 * forward_vel  # Increased from 1.0 to 2.0
            
            # 2. Height maintenance (stay upright, not too strict)
            target_height = 0.75
            height_diff = abs(base_height - target_height)
            height_reward = -2.0 * height_diff  # Penalty for deviation
            
            # 3. Upright orientation (quaternion w should be close to 1)
            # w component of quaternion (1.0 = perfectly upright)
            upright_reward = 1.0 * (base_quat[0] - 1.0)**2  # Squared error
            upright_reward = -upright_reward
            
            # 4. Alive bonus (encourage not falling)
            alive_bonus = 1.0 if base_height > 0.4 else 0.0
            
            # 5. Energy efficiency (penalize excessive joint accelerations)
            energy_penalty = -0.0005 * np.sum(np.square(joint_vel))
            
            # 6. Lateral stability (penalize sideways movement)
            lateral_vel = abs(base_vel[1])  # y-velocity
            lateral_penalty = -0.5 * lateral_vel
            
            # 7. Torso yaw stability (penalize spinning)
            yaw_vel = abs(base_vel[5])  # Angular velocity around z
            yaw_penalty = -0.5 * yaw_vel
            
            # Total reward
            reward = (forward_reward + height_reward + upright_reward + 
                     alive_bonus + energy_penalty + lateral_penalty + yaw_penalty)
            
        else:  # balance
            # Simple balance reward
            reward = -abs(base_height - 0.75)
        
        return reward
    
    def _is_terminated(self, info):
        """Check if episode should terminate"""
        base_height = info['base_height']
        
        # Terminate if robot falls
        if base_height < 0.3:
            return True
        
        return False
    
    
    def render(self):
        """Render environment"""
        if self.render_mode == 'human':
            if self.viewer is None:
                # Use new MuJoCo viewer API for version 3.x
                import mujoco.viewer as viewer
                self.viewer = viewer.launch_passive(self.model, self.data)
            else:
                self.viewer.sync()
        elif self.render_mode == 'rgb_array':
            # Render to RGB array
            renderer = mujoco.Renderer(self.model, height=480, width=640)
            renderer.update_scene(self.data)
            return renderer.render()
        
        return None
    
    def close(self):
        """Clean up resources"""
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None



# Test the environment
if __name__ == '__main__':
    env = G1MuJoCoEnv(task='stand', render_mode='human')
    
    print("\nTesting RL environment...")
    print("Running random actions for 1000 steps\n")
    
    obs, info = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    print(f"Initial base height: {info['base_height']:.3f}")
    
    total_reward = 0
    for i in range(1000):
        # Random action
        action = env.action_space.sample()
        
        # Step environment
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        # Render
        env.render()
        
        if terminated or truncated:
            print(f"Episode finished at step {i+1}")
            print(f"Total reward: {total_reward:.3f}")
            obs, info = env.reset()
            total_reward = 0
    
    env.close()
    print("\nTest complete!")
