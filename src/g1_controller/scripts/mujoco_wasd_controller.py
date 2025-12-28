#!/usr/bin/env python3

"""
MuJoCo WASD Controller for Unitree G1
Controls the G1 robot in MuJoCo using WASD keyboard input
"""

import time
import math
import numpy as np
import sys

try:
    from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_  # Default constructor
    SDK2_AVAILABLE = True
except ImportError:
    print("Error: unitree_sdk2py not available.")
    print("Please install: pip3 install -e ~/unitree_sdk2_python")
    sys.exit(1)

try:
    from pynput import keyboard
except ImportError:
    print("Error: pynput not installed.")
    print("Please install: pip3 install pynput")
    sys.exit(1)


class MuJoCoWASDController:
    """WASD Keyboard Controller for G1 in MuJoCo"""
    
    def __init__(self):
        """Initialize the controller"""
        # Initialize SDK2 framework FIRST
        ChannelFactoryInitialize(0)  # 0 = use default domain ID
        
        # Now create publisher
        self.lowcmd_publisher = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher.Init()
        
        print("✓ SDK2 framework initialized")
        print("✓ SDK2 publisher initialized")
        print("  Publishing to: rt/lowcmd")
        
        # G1 has 29 DOF (joints), matching the ROS2 control setup
        self.num_joints = 29
        
        # Joint names (for reference)
        self.joint_names = [
            'left_hip_pitch_joint', 'left_hip_roll_joint', 'left_hip_yaw_joint',
            'left_knee_joint', 'left_ankle_pitch_joint', 'left_ankle_roll_joint',
            'right_hip_pitch_joint', 'right_hip_roll_joint', 'right_hip_yaw_joint',
            'right_knee_joint', 'right_ankle_pitch_joint', 'right_ankle_roll_joint',
            'waist_yaw_joint', 'waist_roll_joint', 'waist_pitch_joint',
            'left_shoulder_pitch_joint', 'left_shoulder_roll_joint', 'left_shoulder_yaw_joint',
            'left_elbow_joint', 'left_wrist_roll_joint', 'left_wrist_pitch_joint', 'left_wrist_yaw_joint',
            'right_shoulder_pitch_joint', 'right_shoulder_roll_joint', 'right_shoulder_yaw_joint',
            'right_elbow_joint', 'right_wrist_roll_joint', 'right_wrist_pitch_joint', 'right_wrist_yaw_joint',
        ]
        
        # Control parameters
        self.kp = 50.0   # Position gain
        self.kd = 1.0    # Damping gain
        
        # Current motion state
        self.current_motion = None
        self.motion_phase = 0.0
        self.running = True
        
        print("✓ Controller initialized")
    
    def get_standing_pose(self):
        """Return standing pose joint positions"""
        pose = np.zeros(self.num_joints)
        
        # Leg indices (matching joint_names order)
        left_hip_pitch = 0
        left_hip_roll = 1
        left_knee = 3
        left_ankle_pitch = 4
        
        right_hip_pitch = 6
        right_hip_roll = 7
        right_knee = 9
        right_ankle_pitch = 10
        
        # Waist
        waist_yaw = 12
        
        # Arms
        left_shoulder_pitch = 15
        left_shoulder_roll = 16
        left_elbow = 18
        
        right_shoulder_pitch = 22
        right_shoulder_roll = 23
        right_elbow = 25
        
        # Set standing pose (matching Gazebo WASD controller)
        pose[left_hip_pitch] = -0.4
        pose[left_knee] = 0.8
        pose[left_ankle_pitch] = -0.4
        
        pose[right_hip_pitch] = -0.4
        pose[right_knee] = 0.8
        pose[right_ankle_pitch] = -0.4
        
        pose[left_shoulder_pitch] = 0.3
        pose[left_shoulder_roll] = 0.15
        pose[left_elbow] = 0.5
        
        pose[right_shoulder_pitch] = 0.3
        pose[right_shoulder_roll] = -0.15
        pose[right_elbow] = 0.5
        
        return pose
    
    def get_walk_forward_pose(self, phase):
        """Return walking forward pose based on phase"""
        pose = self.get_standing_pose()
        
        # Indices
        left_hip_pitch = 0
        left_knee = 3
        left_shoulder_pitch = 15
        
        right_hip_pitch = 6
        right_knee = 9
        right_shoulder_pitch = 22
        
        # Alternating leg swing
        swing = 1.2 * math.sin(phase)
        
        pose[left_hip_pitch] = -0.4 + swing
        pose[right_hip_pitch] = -0.4 - swing
        pose[left_knee] = 0.8 + max(0, swing * 0.5)
        pose[right_knee] = 0.8 + max(0, -swing * 0.5)
        
        # Arm swing opposite to legs
        pose[left_shoulder_pitch] = 0.3 - swing * 2.5
        pose[right_shoulder_pitch] = 0.3 + swing * 2.5
        
        return pose
    
    def get_walk_backward_pose(self, phase):
        """Return walking backward pose"""
        pose = self.get_standing_pose()
        
        # Indices
        left_hip_pitch = 0
        left_knee = 3
        left_shoulder_pitch = 15
        
        right_hip_pitch = 6
        right_knee = 9
        right_shoulder_pitch = 22
        
        # Reverse leg swing
        swing = 1.2 * math.sin(phase)
        
        pose[left_hip_pitch] = -0.4 - swing
        pose[right_hip_pitch] = -0.4 + swing
        pose[left_knee] = 0.8 + max(0, -swing * 0.5)
        pose[right_knee] = 0.8 + max(0, swing * 0.5)
        
        # Arm swing
        pose[left_shoulder_pitch] = 0.3 + swing * 2.5
        pose[right_shoulder_pitch] = 0.3 - swing * 2.5
        
        return pose
    
    def get_turn_clockwise_pose(self, phase):
        """Return turning clockwise pose"""
        pose = self.get_standing_pose()
        
        # Indices
        waist_yaw = 12
        left_hip_yaw = 2
        right_hip_yaw = 8
        
        # Torso rotation
        pose[waist_yaw] = -1.5 * math.sin(phase)
        
        # Leg movement
        swing = 0.9 * math.sin(phase)
        pose[left_hip_yaw] = -swing
        pose[right_hip_yaw] = swing
        
        return pose
    
    def get_turn_counterclockwise_pose(self, phase):
        """Return turning counter-clockwise pose"""
        pose = self.get_standing_pose()
        
        # Indices
        waist_yaw = 12
        left_hip_yaw = 2
        right_hip_yaw = 8
        
        # Torso rotation
        pose[waist_yaw] = 1.5 * math.sin(phase)
        
        # Leg movement
        swing = 0.9 * math.sin(phase)
        pose[left_hip_yaw] = swing
        pose[right_hip_yaw] = -swing
        
        return pose
    
    def send_command(self, positions, velocities=None):
        """Send low-level motor command via SDK2"""
        cmd = unitree_hg_msg_dds__LowCmd_()  # Use default constructor
        
        if velocities is None:
            velocities = np.zeros(self.num_joints)
        
        # Fill motor commands
        for i in range(min(self.num_joints, len(cmd.motor_cmd))):
            cmd.motor_cmd[i].q = float(positions[i])
            cmd.motor_cmd[i].dq = float(velocities[i])
            cmd.motor_cmd[i].kp = self.kp
            cmd.motor_cmd[i].kd = self.kd
            cmd.motor_cmd[i].tau = 0.0  # Feedforward torque
        
        # Publish command
        self.lowcmd_publisher.Write(cmd)
    
    def control_loop(self):
        """Main control loop"""
        print("\n✓ Control loop started")
        
        while self.running:
            if self.current_motion:
                # Increment phase
                self.motion_phase += 0.1
                if self.motion_phase > 2 * math.pi:
                    self.motion_phase = 0.0
                
                # Get pose based on current motion
                if self.current_motion == 'forward':
                    pose = self.get_walk_forward_pose(self.motion_phase)
                elif self.current_motion == 'backward':
                    pose = self.get_walk_backward_pose(self.motion_phase)
                elif self.current_motion == 'left':
                    pose = self.get_turn_counterclockwise_pose(self.motion_phase)
                elif self.current_motion == 'right':
                    pose = self.get_turn_clockwise_pose(self.motion_phase)
                elif self.current_motion == 'stand':
                    pose = self.get_standing_pose()
                    self.current_motion = None  # One-shot command
                else:
                    pose = self.get_standing_pose()
                
                # Send command
                self.send_command(pose)
            else:
                # Hold standing pose
                pose = self.get_standing_pose()
                self.send_command(pose)
            
            time.sleep(0.05)  # 20 Hz control rate
    
    def start_keyboard_listener(self):
        """Start listening for keyboard input"""
        
        def on_press(key):
            try:
                # Handle character keys
                if hasattr(key, 'char'):
                    if key.char == 'w':
                        self.current_motion = 'forward'
                        self.motion_phase = 0.0
                        print('🚶 Walking FORWARD')
                    elif key.char == 's':
                        self.current_motion = 'backward'
                        self.motion_phase = 0.0
                        print('🚶 Walking BACKWARD')
                    elif key.char == 'a':
                        self.current_motion = 'left'
                        self.motion_phase = 0.0
                        print('↺ Turning COUNTERCLOCKWISE (LEFT)')
                    elif key.char == 'd':
                        self.current_motion = 'right'
                        self.motion_phase = 0.0
                        print('↻ Turning CLOCKWISE (RIGHT)')
                # Handle special keys
                elif key == keyboard.Key.space:
                    self.current_motion = 'stand'
                    self.motion_phase = 0.0
                    print('🧍 Returning to STAND pose')
                elif key == keyboard.Key.esc:
                    print('ESC pressed - Shutting down...')
                    self.running = False
                    return False  # Stop listener
            except AttributeError:
                pass
        
        def on_release(key):
            # Stop motion when key is released
            if hasattr(key, 'char') and key.char in ['w', 'a', 's', 'd']:
                self.current_motion = None
                print('⏸️  Motion stopped')
        
        # Print instructions
        print("\n" + "="*50)
        print("  MuJoCo WASD Controller - Keyboard Controls")
        print("="*50)
        print("\n  W - Walk Forward")
        print("  S - Walk Backward")
        print("  A - Turn Left (Counterclockwise)")
        print("  D - Turn Right (Clockwise)")
        print("  SPACE - Stand Pose")
        print("  ESC - Quit")
        print("\n" + "="*50)
        print("Press and hold keys to move the robot")
        print("="*50 + "\n")
        
        # Start listener
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
    
    def run(self):
        """Run the controller"""
        self.start_keyboard_listener()
        self.control_loop()


def main():
    print("="*60)
    print("  Unitree G1 MuJoCo WASD Controller")
    print("="*60)
    
    controller = MuJoCoWASDController()
    
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nController stopped")


if __name__ == '__main__':
    main()
