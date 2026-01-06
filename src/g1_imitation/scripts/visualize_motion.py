#!/usr/bin/env python3

"""
Visualize LAFAN motions in MuJoCo (open-loop playback)
"""

import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from lafan_env import G1ImitationEnv
from process_lafan import get_motion_names


def visualize_motion(motion_name, loop=True, speed=1.0):
    """
    Play back LAFAN motion in MuJoCo
    
    Args:
        motion_name: Name of motion to visualize
        loop: Whether to loop the motion
        speed: Playback speed (1.0 = normal, 2.0 = 2x speed)
    """
    
    print("\n" + "="*80)
    print(f"Visualizing LAFAN Motion: {motion_name}")
    print("="*80 + "\n")
    
    # Create environment
    env = G1ImitationEnv(motion_name=motion_name, render_mode='human')
    
    print(f"Motion: {motion_name}")
    print(f"Loop: {loop}")
    print(f"Speed: {speed}x")
    print("\nPress Ctrl+C to stop\n")
    
    fps = 30
    frame_time = (1.0 / fps) / speed
    
    try:
        while True:
            obs, info = env.reset()
            print(f"Playing motion (frame 0/{env.motion_length})...", end="\r", flush=True)
            
            done = False
            frame = 0
            
            while not done:
                # Just render, no actions (open-loop playback of reference)
                # We do this by directly setting the robot to reference pose
                ref_frame = env._get_reference_frame(env.current_frame)
                
                # Set robot to reference
                env.data.qpos[:3] = ref_frame[:3]
                env.data.qpos[3:7] = ref_frame[3:7]
                env.data.qpos[7:37] = ref_frame[7:37]
                
                # Render
                env.render()
                
                # Advance frame
                env.current_frame += 1
                frame += 1
                
                if env.current_frame >= env.motion_length:
                    done = True
                
                print(f"Playing motion (frame {frame}/{env.motion_length})...", end="\r", flush=True)
                
                time.sleep(frame_time)
            
            print(f"\n✓ Motion complete ({frame} frames)")
            
            if not loop:
                break
            
            print("Looping...\n")
            time.sleep(1.0)
    
    except KeyboardInterrupt:
        print("\n\n✓ Visualization stopped")
    finally:
        env.close()


def list_motions():
    """List all available motions"""
    print("\n" + "="*80)
    print("Available LAFAN Motions")
    print("="*80 + "\n")
    
    try:
        motions = get_motion_names()
        
        print(f"Found {len(motions)} motions:\n")
        
        for i, motion in enumerate(motions, 1):
            print(f"{i:3d}. {motion}")
        
        print(f"\nTotal: {len(motions)} motions")
        print("\nUsage:")
        print("  python3 scripts/visualize_motion.py --motion <name>")
        print("\n")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("\nRun first:")
        print("  1. python3 scripts/download_lafan.py")
        print("  2. python3 scripts/process_lafan.py\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Visualize LAFAN motions')
    parser.add_argument('--motion', type=str, default=None,
                        help='Motion name to visualize')
    parser.add_argument('--list', action='store_true',
                        help='List all available motions')
    parser.add_argument('--no-loop', action='store_true',
                        help='Play once (no looping)')
    parser.add_argument('--speed', type=float, default=1.0,
                        help='Playback speed (default: 1.0)')
    
    args = parser.parse_args()
    
    if args.list:
        list_motions()
    elif args.motion:
        visualize_motion(args.motion, loop=not args.no_loop, speed=args.speed)
    else:
        print("Error: Specify --motion <name> or --list")
        print("\nExample:")
        print("  python3 scripts/visualize_motion.py --list")
        print("  python3 scripts/visualize_motion.py --motion walk1")
        sys.exit(1)


if __name__ == '__main__':
    main()
