import sys
if sys.prefix == '/home/irman/micromamba/envs/ros2_env':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/irman/Humanoid-VLA-Simulations/install/ros2controlcli'
