#!/usr/bin/env python3
"""
Simple balance demonstration - just hold standing pose
Shows the robot can stand stably with proper PD gains
"""

import time
import numpy as np
from unitree_sdk2py.core.channel import Channel Publisher, ChannelFactoryInitialize
from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_
from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_

# Initialize SDK2
ChannelFactoryInitialize(0)

# Create publisher
pub = ChannelPublisher("rt/lowcmd", LowCmd_)
pub.Init()

print("Balance test - robot will just stand")
print("Press Ctrl+C to stop\n")

# Standing pose
standing_pose = np.zeros(29)
standing_pose[0] = -0.3   # left_hip_pitch
standing_pose[3] = 0.6    # left_knee
standing_pose[4] = -0.3   # left_ankle_pitch
standing_pose[6] = -0.3   # right_hip_pitch
standing_pose[9] = 0.6    # right_knee
standing_pose[10] = -0.3  # right_ankle_pitch

try:
    while True:
        cmd = unitree_hg_msg_dds__LowCmd_()
        
        for i in range(29):
            cmd.motor_cmd[i].q = float(standing_pose[i])
            cmd.motor_cmd[i].dq = 0.0
            cmd.motor_cmd[i].kp = 50.0  # From Unitree example
            cmd.motor_cmd[i].kd = 3.5   # From Unitree example
            cmd.motor_cmd[i].tau = 0.0
        
        pub.Write(cmd)
        time.sleep(0.05)  # 20 Hz

except KeyboardInterrupt:
    print("\nStopped")
