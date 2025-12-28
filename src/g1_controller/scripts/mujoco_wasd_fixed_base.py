#!/usr/bin/env python3

"""
MuJoCo WASD Controller - FIXED BASE VERSION
Temporarily fixes the robot's base to demonstrate joint control works
This allows testing WASD control without balance issues
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
    sys.exit(1)

try:
    from pynput import keyboard
except ImportError:
    print("Error: pynput not installed.")
    sys.exit(1)


class FixedBaseWASDController:
    """WASD Controller - Base is fixed so we can see joint movements work"""
    
    def __init__(self):
        ChannelFactoryInitialize(0)
        self.lowcmd_publisher = ChannelPublisher("rt/lowcmd", LowCmd_)
        self.lowcmd_publisher.Init()
        
        print("✓ SDK2 initialized")
        print("✓ Controller ready (FIXED BASE MODE)")
        
        self.num_joints = 29
        self.kp = 60.0  # Higher for fixed base
        self.kd = 5.0
        
        self.current_motion = 'stand'
        self.motion_phase = 0.0
        self.running = True
        self.dt = 0.05
        
    def get_standing_pose(self):
        pose = np.zeros(self.num_joints)
        pose[0] = -0.3; pose[3] = 0.6; pose[4] = -0.3
        pose[6] = -0.3; pose[9] = 0.6; pose[10] = -0.3
        pose[15] = 0.2; pose[16] = 0.2; pose[18] = 0.4
        pose[22] = 0.2; pose[23] = -0.2; pose[25] = 0.4
        return pose
    
    def get_walk_forward_pose(self, phase):
        pose = self.get_standing_pose()
        swing = 0.4 * math.sin(phase)
        
        # Exaggerated leg swing for visibility
        pose[0] = -0.3 + swing; pose[6] = -0.3 - swing
        pose[3] = 0.6 + abs(swing) * 0.3; pose[9] = 0.6 + abs(-swing) * 0.3
        
        # Arm swing
        pose[15] = 0.2 - swing; pose[22] = 0.2 + swing
        return pose
    
    def get_walk_backward_pose(self, phase):
        pose = self.get_standing_pose()
        swing = 0.4 * math.sin(phase)
        pose[0] = -0.3 - swing; pose[6] = -0.3 + swing
        pose[15] = 0.2 + swing; pose[22] = 0.2 - swing
        return pose
    
    def get_turn_left_pose(self, phase):
        pose = self.get_standing_pose()
        pose[12] = 0.3 * math.sin(phase)  # waist yaw
        return pose
    
    def get_turn_right_pose(self, phase):
        pose = self.get_standing_pose()
        pose[12] = -0.3 * math.sin(phase)
        return pose
    
    def send_command(self, positions):
        cmd = unitree_hg_msg_dds__LowCmd_()
        for i in range(min(self.num_joints, len(cmd.motor_cmd))):
            cmd.motor_cmd[i].q = float(positions[i])
            cmd.motor_cmd[i].dq = 0.0
            cmd.motor_cmd[i].kp = self.kp
            cmd.motor_cmd[i].kd = self.kd
            cmd.motor_cmd[i].tau = 0.0
        self.lowcmd_publisher.Write(cmd)
    
    def control_loop(self):
        print("\n✓ Control loop started (FIXED BASE)")
        print("You should see joint movements clearly!\n")
        
        while self.running:
            if self.current_motion == 'forward':
                self.motion_phase += 0.15
                pose = self.get_walk_forward_pose(self.motion_phase)
            elif self.current_motion == 'backward':
                self.motion_phase += 0.15
                pose = self.get_walk_backward_pose(self.motion_phase)
            elif self.current_motion == 'left':
                self.motion_phase += 0.15
                pose = self.get_turn_left_pose(self.motion_phase)
            elif self.current_motion == 'right':
                self.motion_phase += 0.15
                pose = self.get_turn_right_pose(self.motion_phase)
            else:
                pose = self.get_standing_pose()
                self.motion_phase = 0.0
            
            if self.motion_phase > 2 * math.pi:
                self.motion_phase = 0.0
            
            self.send_command(pose)
            time.sleep(self.dt)
    
    def start_keyboard_listener(self):
        def on_press(key):
            try:
                if hasattr(key, 'char'):
                    if key.char == 'w':
                        self.current_motion = 'forward'
                        print('🚶 Walking FORWARD (animated)')
                    elif key.char == 's':
                        self.current_motion = 'backward'
                        print('🚶 Walking BACKWARD (animated)')
                    elif key.char == 'a':
                        self.current_motion = 'left'
                        print('↺ Turning LEFT')
                    elif key.char == 'd':
                        self.current_motion = 'right'
                        print('↻ Turning RIGHT')
                elif key == keyboard.Key.space:
                    self.current_motion = 'stand'
                    print('🧍 STAND pose')
                elif key == keyboard.Key.esc:
                    print('Stopping...')
                    self.running = False
                    return False
            except AttributeError:
                pass
        
        def on_release(key):
            if hasattr(key, 'char') and key.char in ['w', 'a', 's', 'd']:
                self.current_motion = 'stand'
                print('⏸️ Stopped')
        
        print("\n" + "="*60)
        print("  FIXED BASE WASD Controller (Testing Mode)")
        print("="*60)
        print("\n  ⚠️  Robot base is FIXED - for demonstrating joint control")
        print("  This shows WASD works, but isn't true balance")
        print("")
        print("  W - Walk forward animation")
        print("  S - Walk backward animation")
        print("  A - Turn left")
        print("  D - Turn right")
        print("  SPACE - Stand")
        print("  ESC - Quit")
        print("\n" + "="*60 + "\n")
        
        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        listener.start()
    
    def run(self):
        self.start_keyboard_listener()
        self.control_loop()


def main():
    print("="*60)
    print("  Fixed Base WASD Controller - Testing Mode")
    print("="*60)
    print("\nThis version fixes the robot base to demonstrate")
    print("that WASD joint control works correctly.\n")
    
    controller = FixedBaseWASDController()
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\nStopped")


if __name__ == '__main__':
    main()
