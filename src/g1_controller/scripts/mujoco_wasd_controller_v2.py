#!/usr/bin/env python3

"""
Improved MuJoCo WASD Controller for Unitree G1 with Better Balance Control
Based on official Unitree examples with proper PD gains
"""

import time
import math
import numpy as np
import sys

try:
    from unitree_sdk2py.core.channel import ChannelPublisher, ChannelFactoryInitialize
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
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


class ImprovedWASDController:
    """Improved WASD Controller with proper balance control"""
    
    def __init__(self):
        """Initialize the controller"""
        # Initialize SDK2 framework FIRST
        ChannelFactoryInitialize(0)
        
        # Create publisher
        self.lowcmd_publisher = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher.Init()
        
        print("✓ SDK2 framework initialized")
        print("✓ SDK2 publisher initialized")
        print("  Publishing to: rt/lowcmd")
        
        # G1 has 29 DOF
        self.num_joints = 29
        
        # Control parameters (matching Unitree official examples)
        self.kp = 50.0   # Position gain (from Unitree example)
        self.kd = 3.5    # Damping gain (from Unitree example)
        
        # Current state
        self.current_motion = 'stand'
        self.motion_time = 0.0
        self.running = True
        self.dt = 0.05  # 20 Hz control rate
        
        # Target pose
        self.target_pose = self._get_standing_pose()
        self.current_pose = self._get_standing_pose().copy()
        
        print("✓ Controller initialized")
    
    def _get_standing_pose(self):
        """Return stable standing pose"""
        pose = np.zeros(self.num_joints)
        
        # Legs - keep robot stable
        pose[0] = -0.3   # left_hip_pitch (less bend for stability)
        pose[3] = 0.6    # left_knee (less bend for stability)
        pose[4] = -0.3   # left_ankle_pitch
        
        pose[6] = -0.3   # right_hip_pitch
        pose[9] = 0.6    # right_knee
        pose[10] = -0.3  # right_ankle_pitch
        
        # Arms - down for balance
        pose[15] = 0.0   # left_shoulder_pitch
        pose[16] = 0.3   # left_shoulder_roll (out from body)
        pose[18] = 0.3   # left_elbow (slight bend)
        
        pose[22] = 0.0   # right_shoulder_pitch
        pose[23] = -0.3  # right_shoulder_roll
        pose[25] = 0.3   # right_elbow
        
        return pose
    
    def _get_walk_forward_target(self):
        """Small wrist shift to indicate forward intention"""
        pose = self._get_standing_pose()
        # Very subtle waist pitch for forward lean
        pose[14] = -0.1  # waist_pitch - slight forward lean
        return pose
    
    def _get_walk_backward_target(self):
        """Small shift for backward"""
        pose = self._get_standing_pose()
        pose[14] = 0.1  # waist_pitch - slight backward lean
        return pose
    
    def _get_turn_left_target(self):
        """Slight waist rotation for turning"""
        pose = self._get_standing_pose()
        pose[12] = 0.2  # waist_yaw - turn left
        return pose
    
    def _get_turn_right_target(self):
        """Slight waist rotation for turning"""
        pose = self._get_standing_pose()
        pose[12] = -0.2  # waist_yaw - turn right
        return pose
    
    def send_command(self, positions):
        """Send low-level motor command with proper PD gains"""
        cmd = unitree_hg_msg_dds__LowCmd_()
        
        velocities = np.zeros(self.num_joints)
        
        # Fill motor commands with proper gains
        for i in range(min(self.num_joints, len(cmd.motor_cmd))):
            cmd.motor_cmd[i].q = float(positions[i])
            cmd.motor_cmd[i].dq = float(velocities[i])
            cmd.motor_cmd[i].kp = self.kp  # 50.0 from Unitree example
            cmd.motor_cmd[i].kd = self.kd  # 3.5 from Unitree example
            cmd.motor_cmd[i].tau = 0.0
        
        # Publish
        self.lowcmd_publisher.Write(cmd)
    
    def control_loop(self):
        """Main control loop with smooth transitions"""
        print("\n✓ Control loop started")
        print("Robot will maintain standing pose and make subtle movements\n")
        
        while self.running:
            # Determine target based on current motion
            if self.current_motion == 'forward':
                target = self._get_walk_forward_target()
            elif self.current_motion == 'backward':
                target = self._get_walk_backward_target()
            elif self.current_motion == 'left':
                target = self._get_turn_left_target()
            elif self.current_motion == 'right':
                target = self._get_turn_right_target()
            else:  # stand
                target = self._get_standing_pose()
            
            # Smooth transition to target (interpolation)
            alpha = 0.1  # Smoothing factor
            self.current_pose = (1 - alpha) * self.current_pose + alpha * target
            
            # Send command
            self.send_command(self.current_pose)
            
            self.motion_time += self.dt
            time.sleep(self.dt)
    
    def start_keyboard_listener(self):
        """Start listening for keyboard input"""
        
        def on_press(key):
            try:
                if hasattr(key, 'char'):
                    if key.char == 'w':
                        self.current_motion = 'forward'
                        print('↑ Leaning FORWARD')
                    elif key.char == 's':
                        self.current_motion = 'backward'
                        print('↓ Leaning BACKWARD')
                    elif key.char == 'a':
                        self.current_motion = 'left'
                        print('↺ Turning LEFT')
                    elif key.char == 'd':
                        self.current_motion = 'right'
                        print('↻ Turning RIGHT')
                elif key == keyboard.Key.space:
                    self.current_motion = 'stand'
                    print('🧍 Returning to STAND')
                elif key == keyboard.Key.esc:
                    print('ESC pressed - Shutting down...')
                    self.running = False
                    return False
            except AttributeError:
                pass
        
        def on_release(key):
            if hasattr(key, 'char') and key.char in ['w', 'a', 's', 'd']:
                self.current_motion = 'stand'
                print('⏸️  Returning to stand')
        
        # Print instructions
        print("\n" + "="*60)
        print("  Improved MuJoCo WASD Controller")
        print("="*60)
        print("\n  NOTE: Robot will make SUBTLE movements to maintain balance")
        print("  This is NOT walking - use RL training for actual walking")
        print("")
        print("  W - Lean forward")
        print("  S - Lean backward")
        print("  A - Turn left (waist)")
        print("  D - Turn right (waist)")
        print("  SPACE - Stand pose")
        print("  ESC - Quit")
        print("\n" + "="*60)
        print("Press and hold keys for movement")
        print("="*60 + "\n")
        
        # Start listener
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
    
    def run(self):
        """Run the controller"""
        self.start_keyboard_listener()
        self.control_loop()


def main():
    print("="*60)
    print("  Unitree G1 Improved MuJoCo Controller")
    print("="*60)
    print("\nThis controller uses proper PD gains for stability.")
    print("Robot will make subtle movements while maintaining balance.\n")
    
    controller = ImprovedWASDController()
    
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nController stopped")


if __name__ == '__main__':
    main()
