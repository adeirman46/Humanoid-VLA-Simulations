#!/usr/bin/env python3
"""
Quick test: Run simulator with GUI and controller together
"""

import subprocess
import time
import os

workspace_dir = "/home/irman/Humanoid-VLA-Simulations"

print("="*60)
print("  MuJoCo G1 Quick Test")
print("="*60)
print("\nStarting simulator with GUI...")

# Start simulator in background
sim_cmd = f"cd {workspace_dir} && eval \"$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_g1_simulator.py"
sim_proc = subprocess.Popen(sim_cmd, shell=True, executable='/bin/bash')

print("Waiting 3 seconds for simulator to start...")
time.sleep(3)

print("\nNow starting WASD controller...")
print("Press W/A/S/D to move the robot")
print("Press Ctrl+C to quit\n")

# Run controller in foreground
controller_cmd = f"cd {workspace_dir} && eval \"$(micromamba shell hook --shell bash)\" && micromamba activate ros2_env && python3 src/g1_controller/scripts/mujoco_wasd_controller.py"

try:
    subprocess.run(controller_cmd, shell=True, executable='/bin/bash')
except KeyboardInterrupt:
    print("\nStopping...")

# Clean up simulator
sim_proc.terminate()
sim_proc.wait()
print("Done!")
