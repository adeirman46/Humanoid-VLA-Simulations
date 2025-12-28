#!/usr/bin/env python3

"""
MuJoCo G1 Robot Simulator
Loads the Unitree G1 robot in MuJoCo and provides SDK2-compatible interface
"""

import mujoco
import mujoco.viewer
import numpy as np
import time
import os
import sys
import argparse

try:
    from unitree_sdk2py.core.channel import ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_  # Default constructors
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_
    SDK2_AVAILABLE = True
except ImportError:
    print("Warning: unitree_sdk2py not available. Running in standalone mode.")
    SDK2_AVAILABLE = False


class MuJoCoG1Simulator:
    """MuJoCo simulator for Unitree G1 robot with SDK2 integration"""
    
    def __init__(self, model_path=None, use_sdk2=True, headless=False):
        """
        Initialize the MuJoCo G1 simulator
        
        Args:
            model_path: Path to the G1 MJCF model file
            use_sdk2: Enable SDK2 communication
            headless: Run without visualization
        """
        self.use_sdk2 = use_sdk2 and SDK2_AVAILABLE
        self.headless = headless
        
        # Find model path
        if model_path is None:
            # Try to find unitree_mujoco repository
            home_dir = os.path.expanduser("~")
            model_path = os.path.join(home_dir, "unitree_mujoco/unitree_robots/g1/scene.xml")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(
                    f"Could not find G1 model at {model_path}. "
                    "Please provide model_path or ensure unitree_mujoco is cloned to ~/unitree_mujoco"
                )
        
        print(f"Loading model from: {model_path}")
        
        # Load MuJoCo model
        self.model = mujoco.MjModel.from_xml_path(model_path)
        self.data = mujoco.MjData(self.model)
        
        # Get motor information
        self.num_motors = self.model.nu  # Number of actuators
        print(f"Model loaded: {self.num_motors} actuators")
        
        # Print actuator names for debugging
        print("\nActuator names:")
        for i in range(self.num_motors):
            actuator_id = i
            actuator_name = mujoco.mj_id2name(self.model, mujoco.mjtObj.mjOBJ_ACTUATOR, actuator_id)
            print(f"  {i}: {actuator_name}")
        
        # Control buffers - initialize to standing pose
        self.desired_torque = np.zeros(self.num_motors)
        self.desired_position = self._get_standing_pose()  # Start in standing pose!
        self.desired_velocity = np.zeros(self.num_motors)
        self.kp = np.ones(self.num_motors) * 50.0  # Position gains
        self.kd = np.ones(self.num_motors) * 1.0   # Damping gains
        
        # Set initial joint positions to standing pose
        print("\nInitializing robot to standing pose...")
        self._set_initial_pose()
        
        # Initialize SDK2 communication if enabled
        if self.use_sdk2:
            self.init_sdk2()
        
        # Simulation state
        self.running = True
        self.last_publish_time = 0
        self.publish_rate = 500  # Hz (matching unitree_mujoco default)
        
    
    def _get_standing_pose(self):
        """Get standing pose joint positions (matching WASD controller)"""
        pose = np.zeros(self.num_motors)
        
        # Legs - indices match the actuator order
        pose[0] = -0.4  # left_hip_pitch
        pose[3] = 0.8   # left_knee
        pose[4] = -0.4  # left_ankle_pitch
        
        pose[6] = -0.4  # right_hip_pitch
        pose[9] = 0.8   # right_knee
        pose[10] = -0.4 # right_ankle_pitch
        
        # Arms
        pose[15] = 0.3  # left_shoulder_pitch
        pose[16] = 0.15 # left_shoulder_roll
        pose[18] = 0.5  # left_elbow
        
        pose[22] = 0.3  # right_shoulder_pitch
        pose[23] = -0.15 # right_shoulder_roll
        pose[25] = 0.5  # right_elbow
        
        return pose
    
    def _set_initial_pose(self):
        """Set robot to standing pose in MuJoCo"""
        # Set base height (floating base is first 7 qpos: xyz + quaternion)
        self.data.qpos[2] = 0.75  # Base z-position for standing
        
        # Set joint positions (skip floating base - 7 qpos DOF)
        qpos_start = 7
        standing_pose = self._get_standing_pose()
        self.data.qpos[qpos_start:qpos_start + self.num_motors] = standing_pose
        
        # Forward kinematics to update state
        mujoco.mj_forward(self.model, self.data)
        print("✓ Robot initialized to standing pose")
    
    def init_sdk2(self):
        """Initialize SDK2 DDS communication"""
        try:
            # Initialize SDK2 framework FIRST
            ChannelFactoryInitialize(0)  # 0 = use default domain ID
            
            # Create publishers and subscribers
            self.lowcmd_subscriber = ChannelSubscriber("rt/lowcmd", LowCmd_)
            self.lowstate_publisher = ChannelPublisher("rt/lowstate", LowState_)
            
            self.lowcmd_subscriber.Init()
            self.lowstate_publisher.Init()
            
            print("SDK2 communication initialized")
            print("  Subscribed to: rt/lowcmd")
            print("  Publishing to: rt/lowstate")
        except Exception as e:
            print(f"Failed to initialize SDK2: {e}")
            self.use_sdk2 = False
    
    def get_state(self):
        """Get current robot state from MuJoCo"""
        state = {
            'q': self.data.qpos.copy(),      # Joint positions
            'dq': self.data.qvel.copy(),     # Joint velocities
            'tau': self.data.ctrl.copy(),    # Current torques
            'time': self.data.time
        }
        return state
    
    def set_control(self, torques=None, positions=None, velocities=None):
        """
        Set motor control commands
        
        Args:
            torques: Desired motor torques
            positions: Desired positions (for PD control)
            velocities: Desired velocities (for PD control)
        """
        if torques is not None:
            self.desired_torque = np.array(torques)
        if positions is not None:
            self.desired_position = np.array(positions)
        if velocities is not None:
            self.desired_velocity = np.array(velocities)
    
    def compute_control(self):
        """Compute control torques using PD controller"""
        # Get current joint states (skip floating base - first 7 DOF)
        qpos_start = 7  # Skip floating base position and orientation
        qvel_start = 6  # Skip floating base velocity
        
        q_actual = self.data.qpos[qpos_start:qpos_start + self.num_motors]
        dq_actual = self.data.qvel[qvel_start:qvel_start + self.num_motors]
        
        # PD control: tau = tau_ff + kp * (q_des - q) + kd * (dq_des - dq)
        position_error = self.desired_position - q_actual
        velocity_error = self.desired_velocity - dq_actual
        
        tau = self.desired_torque + self.kp * position_error + self.kd * velocity_error
        
        # Apply control
        self.data.ctrl[:] = tau
    
    def process_sdk2_commands(self):
        """Process incoming SDK2 commands"""
        if not self.use_sdk2:
            return
        
        # Check for new commands
        msg = self.lowcmd_subscriber.Read()
        if msg is not None:
            # Extract motor commands
            torques = []
            positions = []
            velocities = []
            kp = []
            kd = []
            
            for motor_cmd in msg.motor_cmd:
                torques.append(motor_cmd.tau)
                positions.append(motor_cmd.q)
                velocities.append(motor_cmd.dq)
                kp.append(motor_cmd.kp)
                kd.append(motor_cmd.kd)
            
            # Update control
            if len(torques) == self.num_motors:
                self.desired_torque = np.array(torques)
                self.desired_position = np.array(positions)
                self.desired_velocity = np.array(velocities)
                self.kp = np.array(kp)
                self.kd = np.array(kd)
    
    def publish_sdk2_state(self):
        """Publish robot state via SDK2"""
        if not self.use_sdk2:
            return
        
        current_time = time.time()
        if (current_time - self.last_publish_time) < (1.0 / self.publish_rate):
            return
        
        self.last_publish_time = current_time
        
        # Create state message
        state_msg = unitree_hg_msg_dds__LowState_()  # Use default constructor
        
        # Get joint states (skip floating base)
        qpos_start = 7
        qvel_start = 6
        
        q_actual = self.data.qpos[qpos_start:qpos_start + self.num_motors]
        dq_actual = self.data.qvel[qvel_start:qvel_start + self.num_motors]
        tau_actual = self.data.ctrl
        
        # Fill motor states
        for i in range(min(self.num_motors, len(state_msg.motor_state))):
            state_msg.motor_state[i].q = float(q_actual[i])
            state_msg.motor_state[i].dq = float(dq_actual[i])
            state_msg.motor_state[i].tau_est = float(tau_actual[i])
        
        # Fill IMU data (from base body)
        # IMU typically measures base orientation and angular velocity
        base_quat = self.data.qpos[:4]  # Quaternion (w, x, y, z)
        base_vel = self.data.qvel[:3]   # Linear velocity
        base_gyro = self.data.qvel[3:6] # Angular velocity
        
        state_msg.imu_state.quaternion = base_quat.tolist()
        state_msg.imu_state.gyroscope = base_gyro.tolist()
        state_msg.imu_state.accelerometer = [0.0, 0.0, 9.81]  # Placeholder
        
        # Publish
        self.lowstate_publisher.Write(state_msg)
    
    def step(self, num_steps=1):
        """Advance simulation by num_steps"""
        for _ in range(num_steps):
            # Process SDK2 commands if available
            self.process_sdk2_commands()
            
            # Compute control
            self.compute_control()
            
            # Step simulation
            mujoco.mj_step(self.model, self.data)
            
            # Publish state
            self.publish_sdk2_state()
    
    def run(self):
        """Run simulation with visualization"""
        if self.headless:
            self.run_headless()
        else:
            self.run_with_viewer()
    
    def run_headless(self):
        """Run simulation without visualization"""
        print("\nRunning in headless mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.running:
                self.step()
                time.sleep(self.model.opt.timestep)
        except KeyboardInterrupt:
            print("\nSimulation stopped")
    
    def run_with_viewer(self):
        """Run simulation with MuJoCo viewer"""
        print("\nStarting MuJoCo viewer...")
        print("Press Ctrl+C to stop")
        
        with mujoco.viewer.launch_passive(self.model, self.data) as viewer:
            try:
                while viewer.is_running() and self.running:
                    self.step()
                    viewer.sync()
                    
                    # Slow down to real-time
                    time.sleep(self.model.opt.timestep)
                    
            except KeyboardInterrupt:
                print("\nSimulation stopped")


def main():
    parser = argparse.ArgumentParser(description='MuJoCo G1 Robot Simulator')
    parser.add_argument('--model', type=str, default=None,
                      help='Path to G1 MJCF model file')
    parser.add_argument('--headless', action='store_true',
                      help='Run without visualization')
    parser.add_argument('--no-sdk2', action='store_true',
                      help='Disable SDK2 communication')
    
    args = parser.parse_args()
    
    print("="*60)
    print("  Unitree G1 MuJoCo Simulator")
    print("="*60)
    
    # Create simulator
    sim = MuJoCoG1Simulator(
        model_path=args.model,
        use_sdk2=not args.no_sdk2,
        headless=args.headless
    )
    
    # Run simulation
    sim.run()


if __name__ == '__main__':
    main()
