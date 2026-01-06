#!/usr/bin/env python3
"""
Test script to verify SDK2 communication between simulator and controller
"""

import time
import sys

# Test 1: Can we create SDK2 channels?
print("="*60)
print("Testing SDK2 Communication")
print("="*60)

try:
    from unitree_sdk2py.core.channel import ChannelPublisher, ChannelSubscriber, ChannelFactoryInitialize
    from unitree_sdk2py.idl.unitree_hg.msg.dds_ import LowCmd_, LowState_
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowCmd_
    from unitree_sdk2py.idl.default import unitree_hg_msg_dds__LowState_
    print("✓ SDK2 imports successful")
except ImportError as e:
    print(f"✗ SDK2 import failed: {e}")
    sys.exit(1)

# Initialize SDK2
ChannelFactoryInitialize(0)
print("✓ SDK2 framework initialized")

# Create publisher (like controller)
pub = ChannelPublisher("rt/lowcmd", LowCmd_)
pub.Init()
print("✓ Publisher created (rt/lowcmd)")

# Create subscriber (like simulator)
sub = ChannelSubscriber("rt/lowcmd", LowCmd_)
sub.Init()
print("✓ Subscriber created (rt/lowcmd)")

# Try to send and receive a message
print("\nTesting message passing...")
cmd = unitree_hg_msg_dds__LowCmd_()
cmd.motor_cmd[0].q = 1.23456
cmd.motor_cmd[0].kp = 50.0

print(f"Sending command with motor_cmd[0].q = {cmd.motor_cmd[0].q}")
pub.Write(cmd)
time.sleep(0.1)

# Try to read
received = sub.Read()
if received is not None:
    print(f"✓ Received command! motor_cmd[0].q = {received.motor_cmd[0].q}")
    print("✓ SDK2 communication working!")
else:
    print("✗ No message received - DDS communication may not be working")
    print("  This could be a timing issue or DDS configuration problem")

print("\n" + "="*60)
print("Communication test complete")
print("="*60)
