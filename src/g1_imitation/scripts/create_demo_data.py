#!/usr/bin/env python3

"""
Create demo motion data for testing imitation learning
Since LAFAN retargeted dataset is not publicly available, create synthetic demo
"""

import numpy as np
import pandas as pd
from pathlib import Path


def create_demo_walk_motion(num_frames=300, fps=30):
    """
    Create a simple walking motion (demo/placeholder)
    Format: 37 columns (pelvis pos:3, pelvis quat:4, joints:30)
    """
    
    # Time array
    t = np.linspace(0, num_frames/fps, num_frames)
    
    # Pelvis trajectory (moving forward + bobbing)
    pelvis_x = t * 0.5  # Forward at 0.5 m/s
    pelvis_y = np.zeros(num_frames)
    pelvis_z = 0.75 + 0.02 * np.sin(2 * np.pi * t * 2)  # Slight vertical bob
    
    # Pelvis orientation (upright)
    pelvis_qw = np.ones(num_frames)
    pelvis_qx = np.zeros(num_frames)
    pelvis_qy = np.zeros(num_frames)
    pelvis_qz = np.zeros(num_frames)
    
    # Joint angles (30 joints)
    # Simple sinusoidal pattern for legs (hip, knee, ankle)
    joints = np.zeros((num_frames, 30))
    
    # Left hip pitch (joint 0)
    joints[:, 0] = -0.4 + 0.3 * np.sin(2 * np.pi * t * 2)
    # Left knee (joint 3)
    joints[:, 3] = 0.8 + 0.2 * np.sin(2 * np.pi * t * 2)
    # Left ankle (joint 4)
    joints[:, 4] = -0.4 - 0.1 * np.sin(2 * np.pi * t * 2)
    
    # Right hip pitch (joint 6) - opposite phase
    joints[:, 6] = -0.4 + 0.3 * np.sin(2 * np.pi * t * 2 + np.pi)
    # Right knee (joint 9)
    joints[:, 9] = 0.8 + 0.2 * np.sin(2 * np.pi * t * 2 + np.pi)
    # Right ankle (joint 10)
    joints[:, 10] = -0.4 - 0.1 * np.sin(2 * np.pi * t * 2 + np.pi)
    
    # Combine all
    motion_data = np.column_stack([
        pelvis_x, pelvis_y, pelvis_z,
        pelvis_qw, pelvis_qx, pelvis_qy, pelvis_qz,
        joints
    ])
    
    return motion_data


def create_demo_dataset(output_dir="data/lafan1_retargeted"):
    """Create demo motion files"""
    
    print("\n" + "="*80)
    print("Creating Demo Motion Data")
    print("="*80 + "\n")
    print("Note: LAFAN retargeted dataset not publicly available")
    print("Creating synthetic demo motions for testing\n")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create several demo motions
    motions = {
        'walk1': create_demo_walk_motion(300, 30),
        'walk2': create_demo_walk_motion(250, 30),
        'walk_slow': create_demo_walk_motion(400, 30),
    }
    
    for name, data in motions.items():
        csv_file = output_path / f"{name}.csv"
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False, header=False)
        print(f"✓ Created {name}.csv ({len(data)} frames, {len(data)/30:.1f}s)")
    
    print(f"\n✓ Created {len(motions)} demo motions")
    print(f"Location: {output_path.absolute()}\n")
    
    print("="*80)
    print("Demo dataset ready!")
    print("Next: python3 scripts/process_lafan.py")
    print("="*80 + "\n")


if __name__ == '__main__':
    create_demo_dataset()
