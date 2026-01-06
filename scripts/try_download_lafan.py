#!/usr/bin/env python3
"""Download REAL LAFAN1 dataset - try all possible HuggingFace paths"""

import os
from huggingface_hub import snapshot_download, list_datasets
from pathlib import Path

def try_download_lafan():
    """Try different possible repository paths for LAFAN1"""
    
    # Load token
    token = None
    env_file = Path("huggingface.env")
    if env_file.exists():
        token = env_file.read_text().strip()
    
    print(f"Token loaded: {token[:10]}..." if token else "No token")
    
    # Possible repository paths to try
    possible_repos = [
        "unitreerobotics/LAFAN1_Retargeting_Dataset",
        "UnitreeRobotics/LAFAN1_Retargeting_Dataset", 
        "unitree/LAFAN1_Retargeting_Dataset",
        "Unitree/LAFAN1-retargeting",
        "unitreerobotics/lafan1-retargeting",
        "LAFAN1/retargeting",
    ]
    
    for repo_id in possible_repos:
        print(f"\nTrying: {repo_id}")
        try:
            snapshot_download(
                repo_id=repo_id,
                repo_type="dataset",
                local_dir="src/g1_imitation/data/lafan1_retargeted",
                token=token,
            )
            print(f"✅ SUCCESS: Downloaded from {repo_id}")
            return True
        except Exception as e:
            print(f"❌ Failed: {str(e)[:100]}")
            continue
    
    # If all fail, search for it
    print("\n🔍 Searching HuggingFace for LAFAN...")
    try:
        datasets = list_datasets(search="LAFAN", token=token)
        print(f"Found {len(list(datasets))} datasets matching 'LAFAN':")
        for ds in list(datasets)[:10]:
            print(f"  - {ds.id}")
    except:
        pass
    
    return False

if __name__ == '__main__':
    success = try_download_lafan()
    exit(0 if success else 1)
