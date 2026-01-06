#!/usr/bin/env python3

"""
Download LAFAN1 retargeted dataset from HuggingFace
Pre-retargeted for Unitree G1 robot
"""

import os
import sys
from huggingface_hub import hf_hub_download, snapshot_download
from pathlib import Path


def download_lafan1_retargeted(output_dir="data/lafan1_retargeted"):
    """
    Download LAFAN1 dataset retargeted for Unitree G1
    
    Dataset: huggingface.co/datasets/Unilab-AI/LAFAN1-retargeting
    Format: CSV files with 37 columns (pelvis pose + 30 joints)
    """
    
    print("\n" + "="*80)
    print("Downloading LAFAN1 Retargeted Dataset")
    print("="*80 + "\n")
    
    # Load HuggingFace token from env file
    token = None
    env_file = Path(__file__).parent.parent.parent.parent / "huggingface.env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read().strip()
            # Handle both formats: plain token or HUGGINGFACE_TOKEN=token
            if content.startswith('HUGGINGFACE_TOKEN='):
                token = content.split('=', 1)[1].strip('"').strip("'")
            elif content.startswith('hf_'):
                token = content
            print("✓ Found HuggingFace token")
    
    if not token:
        print("⚠️  No HuggingFace token found in huggingface.env")
        print("This dataset may require authentication")
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Output directory: {output_path.absolute()}\n")
    
    # Dataset info - CORRECTED REPO PATH
    repo_id = "unitreerobotics/LAFAN1_Retargeting_Dataset"
    print(f"Repository: {repo_id}")
    print("Robot: Unitree G1")
    print("Format: CSV (pelvis pose + joints)\n")
    
    try:
        print("Downloading dataset...")
        print("This may take a few minutes (~50MB)\n")
        
        # Download specific folder for G1
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=str(output_path),
            allow_patterns="*.csv",  # Only CSV files
            token=token,  # Use token for authentication
        )
        
        print("\n✓ Download complete!")
        
        # List downloaded files
        csv_files = list(output_path.glob("**/*.csv"))
        print(f"\nDownloaded {len(csv_files)} motion files:")
        
        for csv_file in sorted(csv_files)[:10]:  # Show first 10
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"  • {csv_file.name} ({size_mb:.2f} MB)")
        
        if len(csv_files) > 10:
            print(f"  ... and {len(csv_files) - 10} more files")
        
        print(f"\nTotal files: {len(csv_files)}")
        print(f"Location: {output_path.absolute()}\n")
        
        # Show sample data
        if csv_files:
            print("Sample data structure (first file):")
            import pandas as pd
            sample = pd.read_csv(csv_files[0], nrows=5)
            print(f"  Columns: {len(sample.columns)}")
            print(f"  Expected: 37 (pelvis_pos:3 + pelvis_quat:4 + joints:30)")
            print(f"  Frames: {len(pd.read_csv(csv_files[0]))}")
            print(f"  FPS: 30\n")
        
        print("="*80)
        print("Next steps:")
        print("  1. python3 scripts/process_lafan.py")
        print("  2. python3 scripts/visualize_motion.py")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading dataset: {e}")
        print("\nTroubleshooting:")
        print("  1. Check internet connection")
        print("  2. Verify HuggingFace Hub access")
        print("  3. Try: pip install --upgrade huggingface_hub")
        return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Download LAFAN1 retargeted dataset')
    parser.add_argument('--output-dir', type=str, default='data/lafan1_retargeted',
                        help='Output directory for dataset')
    
    args = parser.parse_args()
    
    success = download_lafan1_retargeted(args.output_dir)
    
    if success:
        print("✅ Dataset ready for processing!")
        sys.exit(0)
    else:
        print("❌ Download failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
