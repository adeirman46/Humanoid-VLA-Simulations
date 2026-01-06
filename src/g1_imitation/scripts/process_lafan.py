#!/usr/bin/env python3

"""
Process LAFAN1 CSV files into structured numpy format for fast loading
"""

import numpy as np
import pandas as pd
from pathlib import Path
import pickle
import json


def process_lafan1(input_dir="data/lafan1_retargeted/g1", output_dir="data/processed"):
    """
    Convert LAFAN1 CSV files to structured numpy arrays
    
    Input: CSV files (frame x columns) - from G1 subfolder
    Output: Dictionary of motion clips as numpy arrays
    """
    
    print("\n" + "="*80)
    print("Processing LAFAN1 Dataset - G1 Robot")
    print("="*80 + "\n")
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    if not input_path.exists():
        print(f"❌ Error: Input directory not found: {input_path}")
        print("\nRun first: python3 scripts/download_lafan.py\n")
        return False
    
    # Find all CSV files in G1 folder
    csv_files = list(input_path.glob("*.csv"))
    
    if not csv_files:
        print(f"❌ No CSV files found in {input_path}")
        return False
    
    print(f"Found {len(csv_files)} motion files in G1 folder\n")
    
    motion_database = {}
    
    for csv_file in sorted(csv_files):
        motion_name = csv_file.stem
        print(f"Processing: {motion_name}...", end=" ")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_file, header=None)
            
            # Convert to numpy
            motion_data = df.values.astype(np.float32)
            
            # Auto-detect format (G1 data varies)
            num_cols = motion_data.shape[1]
            
            # Store with metadata
            motion_database[motion_name] = {
                'data': motion_data,
                'num_frames': len(motion_data),
                'fps': 30,
                'duration': len(motion_data) / 30.0,
                'joints': 30,
            }
            
            print(f"✓ {len(motion_data)} frames ({num_cols} cols)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            continue
    
    print(f"\n✓ Processed {len(motion_database)} motions\n")
    
    # Save as pickle for fast loading
    output_file = output_path / "lafan1_motions.pkl"
    with open(output_file, 'wb') as f:
        pickle.dump(motion_database, f)
    
    print(f"Saved to: {output_file}")
    
    # Save metadata JSON
    metadata = {
        name: {k: v for k, v in info.items() if k != 'data'}
        for name, info in motion_database.items()
    }
    
    metadata_file = output_path / "lafan1_metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"Metadata: {metadata_file}\n")
    
    # Print statistics
    total_frames = sum(m['num_frames'] for m in motion_database.values())
    total_duration = sum(m['duration'] for m in motion_database.values())
    
    print("="*80)
    print("Dataset Statistics:")
    print(f"  Motions: {len(motion_database)}")
    print(f"  Total frames: {total_frames:,}")
    print(f"  Total duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    print(f"  Avg duration: {total_duration/len(motion_database):.1f}s per motion")
    print(f"  FPS: 30")
    print("="*80 + "\n")
    
    # Show sample motions
    print("Sample motions:")
    for name in list(motion_database.keys())[:10]:
        info = motion_database[name]
        print(f"  • {name}: {info['num_frames']} frames ({info['duration']:.1f}s)")
    
    if len(motion_database) > 10:
        print(f"  ... and {len(motion_database) - 10} more")
    
    print("\n" + "="*80)
    print("Next steps:")
    print("  1. python3 scripts/visualize_motion.py")
    print("  2. python3 scripts/train_deepmimic.py")
    print("="*80 + "\n")
    
    return True


def load_motion_database(processed_dir="data/processed"):
    """Load processed motion database"""
    pkl_file = Path(processed_dir) / "lafan1_motions.pkl"
    
    if not pkl_file.exists():
        raise FileNotFoundError(f"Processed data not found: {pkl_file}\nRun: python3 scripts/process_lafan.py")
    
    with open(pkl_file, 'rb') as f:
        return pickle.load(f)


def get_motion_names(processed_dir="data/processed"):
    """Get list of available motion names"""
    database = load_motion_database(processed_dir)
    return sorted(database.keys())


def get_motion(motion_name, processed_dir="data/processed"):
    """Get specific motion data"""
    database = load_motion_database(processed_dir)
    
    if motion_name not in database:
        raise ValueError(f"Motion '{motion_name}' not found. Available: {list(database.keys())[:10]}...")
    
    return database[motion_name]


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Process LAFAN1 dataset')
    parser.add_argument('--input-dir', type=str, default='data/lafan1_retargeted/g1')
    parser.add_argument('--output-dir', type=str, default='data/processed')
    
    args = parser.parse_args()
    
    success = process_lafan1(args.input_dir, args.output_dir)
    
    if success:
        print("✅ Processing complete!")
        return 0
    else:
        print("❌ Processing failed")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
