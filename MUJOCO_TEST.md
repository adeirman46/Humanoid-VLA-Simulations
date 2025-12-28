# Quick Test Script for MuJoCo Setup

This script verifies that the MuJoCo integration is working correctly.

## Test 1: MuJoCo Installation
```bash
python3 -c "import mujoco; print('✓ MuJoCo', mujoco.__version__)"
```

## Test 2: Unitree SDK2
```bash
python3 -c "import unitree_sdk2py; print('✓ Unitree SDK2')"
```

## Test 3: G1 Model Loading
```bash
python3 -c "
import mujoco
import os
model_path = os.path.expanduser('~/unitree_mujoco/unitree_robots/g1/scene.xml')
model = mujoco.MjModel.from_xml_path(model_path)
print(f'✓ G1 model loaded with {model.nu} actuators')
"
```

## Test 4: Simulator (Headless)
```bash
# Run simulator in background for 3 seconds
timeout 3 python3 src/g1_controller/scripts/mujoco_g1_simulator.py --headless --no-sdk2
```

## Test 5: WASD Controller Initialization
```bash
# This should initialize without errors (will timeout waiting for input)
timeout 3 python3 src/g1_controller/scripts/mujoco_wasd_controller.py 2>&1 | grep "✓"
```

Expected output:
```
✓ SDK2 framework initialized
✓ SDK2 publisher initialized
✓ Controller initialized
```

## Test 6: Full System Test
```bash
# This requires two terminals - use the launch script
./launch_mujoco_wasd.sh
```

## Common Issues

### Issue: AttributeError: 'NoneType' object has no attribute '_ref'
**Status:** ✅ FIXED

**Solution:** Updated both scripts to call `ChannelFactoryInitialize(0)` before creating any SDK2 publishers or subscribers.

### Issue: Model not found
**Solution:**
```bash
ls ~/unitree_mujoco/unitree_robots/g1/scene.xml
# If not found, clone:
git clone https://github.com/unitreerobotics/unitree_mujoco.git ~/unitree_mujoco
```

### Issue: pynput not installed
**Solution:**
```bash
pip3 install pynput
```

## All Tests Pass ✅

If all tests above pass, your MuJoCo setup is ready for RL training!
