#!/usr/bin/env python3
import sys
sys.path.append('/home/irman/Humanoid-VLA-Simulations/src/g1_controller/scripts')

from mujoco_rl_env import G1MuJoCoEnv
import time

print('Creating environment with render mode...')
env = G1MuJoCoEnv(task='walk', render_mode='human')
print('✓ Environment created')

obs, info = env.reset()
print('✓ Reset successful')

print('Testing render for 3 seconds...')
for i in range(90):
    env.render()
    time.sleep(0.033)

print('✓ Render working!')
env.close()
print('✓ Test passed!')
