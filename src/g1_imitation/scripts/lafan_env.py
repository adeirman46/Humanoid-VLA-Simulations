#!/usr/bin/env python3

"""
LAFAN Imitation Environment for Unitree G1
DeepMimic-style imitation learning with motion capture reference
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
import mujoco
import os
import sys
from pathlib import Path

# Add processing script to path
sys.path.append(str(Path(__file__).parent))
from process_lafan import load_motion_database, get_motion


class G1ImitationEnv(gym.Env):
    """
    Imitation learning environment - COMPLETELY SEPARATE from mujoco_rl_env.py!
    
    Uses LAFAN1 reference motions with DeepMimic reward
    """
    
    metadata = {'render_modes': ['human', 'rgb_array'], 'render_fps': 30}
    
    def __init__(self, motion_name=None, render_mode=None, data_dir="../data/processed"):
        """
        Args:
            motion_name: Specific motion to train (or None for random sampling)
            render_mode: 'human' or 'rgb_array'
            data_dir: Directory with processed LAFAN data
        """
        super().__init__()
        
        self.render_mode = render_mode
        self.motion_name = motion_name
        
        # Load MuJoCo model
        home_dir = os.path.expanduser("~")
        model_path = os.path.join(home_dir, "unitree_mujoco/unitree_robots/g1/scene.xml")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"G1 model not found: {model_path}")
        
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        
        # Load LAFAN data
        script_dir = Path(__file__).parent
        self.data_dir = script_dir / data_dir
        
        try:
            self.motion_database = load_motion_database(str(self.data_dir))
            print(f"Loaded {len(self.motion_database)} LAFAN motions")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Run first: python3 scripts/process_lafan.py")
            raise
        
        # Current motion
        self.current_motion = None
        self.current_frame = 0
        self.motion_length = 0
        
        # Robot dimensions
        self.num_motors = self.model.nu  # 29
        
        # Observation: robot state + reference frames
        # Robot: joint_pos(29) + joint_vel(29) + root_pos(3) + root_quat(4) = 65
        # Reference current: pelvis(7) + joints(29) = 36  (LAFAN G1 format)
        # Reference next: pelvis(7) + joints(29) = 36
        # Total: 65 + 36 + 36 = 137
        obs_dim = 137  # Updated for actual LAFAN G1 data format
        
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )
        
        # Action: target joint positions
        self.action_space = spaces.Box(
            low=-3.14, high=3.14, shape=(self.num_motors,), dtype=np.float32
        )
        
        # Control parameters
        self.kp = 50.0
        self.kd = 1.0
        
        #Episode parameters
        self.max_episode_steps = 1000
        self.current_step = 0
        
        # Viewer
        self.viewer = None
        
        print(f"G1 Imitation Environment initialized")
        print(f"  Motions: {len(self.motion_database)}")
        print(f"  Obs dim: {obs_dim}")
        print(f"  Action dim: {self.num_motors}")
    
    def _sample_motion(self):
        """Sample a random motion or use specified one"""
        if self.motion_name and self.motion_name in self.motion_database:
            return self.motion_name
        else:
            return np.random.choice(list(self.motion_database.keys()))
    
    def _get_reference_frame(self, frame_idx):
        """Get reference pose at specific frame"""
        if frame_idx >= self.motion_length:
            frame_idx = self.motion_length - 1
        
        frame_data = self.current_motion['data'][frame_idx]
        # LAFAN G1 has 36 columns: pelvis(7) + joints(29)
        return frame_data.astype(np.float32)
    
    def _get_obs(self):
        """Get observation: robot state + reference frames"""
        # Robot state
        qpos_start = 7
        qvel_start = 6
        
        joint_pos = self.data.qpos[qpos_start:qpos_start + self.num_motors]
        joint_vel = self.data.qvel[qvel_start:qvel_start + self.num_motors]
        root_pos = self.data.qpos[:3]
        root_quat = self.data.qpos[3:7]
        
        robot_state = np.concatenate([joint_pos, joint_vel, root_pos, root_quat])
        
        # Reference frames
        ref_current = self._get_reference_frame(self.current_frame)
        ref_next = self._get_reference_frame(self.current_frame + 1)
        
        obs = np.concatenate([robot_state, ref_current, ref_next])
        
        return obs.astype(np.float32)
    
    def _compute_deepmimic_reward(self):
        """
        DeepMimic reward: exponential similarity between robot and reference
        """
        # Get reference pose
        ref_frame = self._get_reference_frame(self.current_frame)
        
        # Extract reference components (36 columns total)
        ref_pelvis_pos = ref_frame[:3]
        ref_pelvis_quat = ref_frame[3:7]
        ref_joints = ref_frame[7:36]  # 29 joints in LAFAN G1 data
        
        # Get robot state (29 actuators)
        robot_pelvis_pos = self.data.qpos[:3]
        robot_pelvis_quat = self.data.qpos[3:7]
        robot_joints = self.data.qpos[7:36]  # 29 joints in robot
        
        # Already matched - both have 29 joints
        
        # 1. Joint position similarity (MAIN component - focus on joint angles!)
        joint_diff = np.sum((robot_joints - ref_joints) ** 2)
        r_pose = np.exp(-2.0 * joint_diff)
        
        # 2. Pelvis position similarity (REDUCED weight - we start at origin)
        # We don't match position exactly, just general direction
        pelvis_pos_diff = np.sum((robot_pelvis_pos - ref_pelvis_pos) ** 2)
        r_pelvis_pos = np.exp(-1.0 * pelvis_pos_diff)  # Reduced from -10.0
        
        # 3. Pelvis orientation similarity (keep torso upright)
        # Quaternion distance
        quat_dot = np.abs(np.dot(robot_pelvis_quat, ref_pelvis_quat))
        r_pelvis_rot = np.exp(-5.0 * (1.0 - quat_dot))
        
        # 4. Velocity matching (penalize excessive velocities)
        vel_penalty = np.exp(-0.1 * np.sum(self.data.qvel ** 2))
        
        # Combined reward - MORE weight on joint angles, LESS on pelvis position
        reward = 0.6 * r_pose + 0.05 * r_pelvis_pos + 0.25 * r_pelvis_rot + 0.1 * vel_penalty
        
        return reward
    
    def reset(self, seed=None, options=None):
        """Reset to random motion and random start frame"""
        super().reset(seed=seed)
        
        # Sample motion
        motion_key = self._sample_motion()
        self.current_motion = self.motion_database[motion_key]
        self.motion_length = self.current_motion['num_frames']
        
        # Sample random start frame (but not too close to end)
        max_start = max(1, self.motion_length - 100)
        self.current_frame = np.random.randint(0, max_start)
        
        # Reset MuJoCo
        mujoco.mj_resetData(self.model, self.data)
        
        # ALWAYS start at ORIGIN on GROUND (not at reference position!)
        # Only copy joint angles from reference, NOT pelvis position
        ref_frame = self._get_reference_frame(self.current_frame)
        
        # Set pelvis to FIXED starting position (origin, on ground)
        self.data.qpos[:3] = [0.0, 0.0, 0.75]  # Fixed: x=0, y=0, z=0.75 (standing height)
        self.data.qpos[3:7] = [1.0, 0.0, 0.0, 0.0]  # Fixed: upright orientation (w,x,y,z)
        
        # Copy only joint angles from reference (NOT pelvis!)
        self.data.qpos[7:36] = ref_frame[7:36]  # Joints only
        
        # Zero velocities
        self.data.qvel[:] = 0.0
        
        # Forward to stabilize
        for _ in range(10):
            mujoco.mj_step(self.model, self.data)
        
        self.current_step = 0
        
        info = {'frame': self.current_frame, 'motion': motion_key}
        
        return self._get_obs(), info
    
    def step(self, action):
        """Execute action and advance reference frame"""
        # Apply PD control
        qpos_start = 7
        qvel_start = 6
        
        q_actual = self.data.qpos[qpos_start:qpos_start + self.num_motors]
        dq_actual = self.data.qvel[qvel_start:qvel_start + self.num_motors]
        
        tau = self.kp * (action - q_actual) + self.kd * (0.0 - dq_actual)
        self.data.ctrl[:] = tau
        
        # Step simulation
        mujoco.mj_step(self.model, self.data)
        
        # Advance reference frame
        self.current_frame += 1
        self.current_step += 1
        
        # Compute reward
        reward = self._compute_deepmimic_reward()
        
        # Check termination
        terminated = self._is_terminated()
        truncated = (self.current_step >= self.max_episode_steps or 
                    self.current_frame >= self.motion_length - 1)
        
        obs = self._get_obs()
        info = {'frame': self.current_frame, 'motion': list(self.motion_database.keys())[0]}
        
        return obs, reward, terminated, truncated, info
    
    def _is_terminated(self):
        """Early termination if robot diverges too much"""
        # Terminate if fallen
        if self.data.qpos[2] < 0.2:
            return True
        
        # Terminate if pose error too large
        ref_frame = self._get_reference_frame(self.current_frame)
        ref_joints = ref_frame[7:36]  # First 29 only
        robot_joints = self.data.qpos[7:36]  # 29 joints
        joint_error = np.sum((robot_joints - ref_joints) ** 2)
        
        if joint_error > 5.0:  # Large deviation
            return True
        
        return False
    
    def render(self):
        """Render environment"""
        if self.render_mode == 'human':
            if self.viewer is None:
                import mujoco.viewer as viewer
                self.viewer = viewer.launch_passive(self.model, self.data)
            else:
                self.viewer.sync()
        elif self.render_mode == 'rgb_array':
            renderer = mujoco.Renderer(self.model, height=480, width=640)
            renderer.update_scene(self.data)
            return renderer.render()
        
        return None
    
    def close(self):
        """Clean up"""
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None


# Test
if __name__ == '__main__':
    print("\n" + "="*60)
    print("Testing G1 Imitation Environment")
    print("="*60 + "\n")
    
    try:
        env = G1ImitationEnv()
        print("✓ Environment created\n")
        
        obs, info = env.reset()
        print(f"✓ Reset successful")
        print(f"  Obs shape: {obs.shape}")
        print(f"  Frame: {info['frame']}\n")
        
        # Test a few steps
        for i in range(5):
            action = env.action_space.sample() * 0.1
            obs, reward, term, trunc, info = env.step(action)
            print(f"Step {i+1}: reward={reward:.4f}, frame={info['frame']}")
        
        print("\n✓ All tests passed!")
        print("Ready for training! 🚀\n")
        
        env.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure to run:")
        print("  1. python3 scripts/download_lafan.py")
        print("  2. python3 scripts/process_lafan.py\n")
