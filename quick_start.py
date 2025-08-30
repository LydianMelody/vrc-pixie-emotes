#!/usr/bin/env python3
"""
Quick Start Script for VRChat GIF Maker

Simple command-line interface for converting GIFs to sprite sheets.
"""

import sys
import os
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.gif_processor import GIFProcessor
from src.sprite_generator import VRChatSpriteGenerator
from src.color_optimizer import ColorOptimizer
from src.utils.filename_parser import FilenameParser
from src.utils.frame_reducer import FrameReducer


def convert_gif(input_path, output_path=None, frames=None, fps=10, 
                strategy='none', optimize_colors=True, max_colors=256):
    """
    Convert a GIF to a VRChat sprite sheet.
    
    Args:
        input_path: Path to input GIF file
        output_path: Path for output sprite sheet (optional)
        frames: Number of frames to include (optional)
        fps: Frames per second (default: 10)
        strategy: Frame reduction strategy (default: 'none')
        optimize_colors: Whether to optimize colors (default: True)
        max_colors: Maximum number of colors (default: 256)
    """
    
    print(f"Loading GIF: {input_path}")
    
    # Load GIF
    gif_processor = GIFProcessor(input_path)
    all_frames = gif_processor.get_frames()
    info = gif_processor.get_frame_info()
    
    print(f"GIF loaded: {info['total_frames']} frames, {info['original_dimensions']}")
    
    # Determine frame count
    if frames is None:
        frames = min(info['total_frames'], 64)
    
    if frames > 64:
        print(f"Warning: Frame count {frames} exceeds VRChat limit of 64")
        frames = 64
    
    # Reduce frames if needed
    if frames < len(all_frames):
        print(f"Reducing frames from {len(all_frames)} to {frames} using '{strategy}' strategy")
        frame_reducer = FrameReducer()
        reduced_frames = frame_reducer.reduce_frames(all_frames, frames, strategy)
    else:
        reduced_frames = all_frames
    
    # Generate sprite sheet
    print("Generating sprite sheet...")
    sprite_generator = VRChatSpriteGenerator()
    sprite_sheet = sprite_generator.create_sprite_sheet(reduced_frames, frames)
    
    # Optimize colors if requested
    if optimize_colors:
        print("Optimizing colors...")
        color_optimizer = ColorOptimizer(max_colors)
        sprite_sheet = color_optimizer.optimize_sprite_sheet(sprite_sheet, max_colors)
        
        # Show optimization stats
        original = sprite_generator.create_sprite_sheet(reduced_frames, frames)
        stats = color_optimizer.get_optimization_stats(original, sprite_sheet)
        print(f"Color optimization: {stats['original_colors']} -> {stats['optimized_colors']} colors")
    
    # Generate output filename if not provided
    if output_path is None:
        filename_parser = FilenameParser()
        base_name = filename_parser.extract_base_name(os.path.basename(input_path))
        output_path = filename_parser.generate_filename(base_name, frames, fps)
    
    # Save sprite sheet
    print(f"Saving sprite sheet: {output_path}")
    sprite_sheet.save(output_path, "PNG", optimize=True)
    
    # Show sprite sheet info
    sheet_info = sprite_generator.get_sprite_sheet_info(frames)
    print(f"\nSprite sheet created successfully!")
    print(f"Size: {sheet_info['sprite_sheet_size'][0]}x{sheet_info['sprite_sheet_size'][1]} pixels")
    print(f"Layout: {sheet_info['layout_name']} grid")
    print(f"Frame size: {sheet_info['frame_size']}x{sheet_info['frame_size']} pixels")
    print(f"Frames: {sheet_info['frame_count']}/{sheet_info['total_cells']}")
    print(f"FPS: {fps}")
    print(f"File: {output_path}")


def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="Convert GIF files to VRChat-compatible sprite sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_start.py animation.gif
  python quick_start.py animation.gif -o output.png -f 16 -r 20
  python quick_start.py animation.gif --frames 8 --fps 15 --strategy uniform
        """
    )
    
    parser.add_argument('input', help='Input GIF file path')
    parser.add_argument('-o', '--output', help='Output sprite sheet path (optional)')
    parser.add_argument('-f', '--frames', type=int, help='Number of frames (1-64, default: all)')
    parser.add_argument('-r', '--fps', type=int, default=10, help='Frames per second (default: 10)')
    parser.add_argument('-s', '--strategy', default='none', 
                       choices=['none', 'keep_ends', 'uniform', 'smart', 'every_nth'],
                       help='Frame reduction strategy (default: none)')
    parser.add_argument('--no-optimize', action='store_true', 
                       help='Disable color optimization')
    parser.add_argument('-c', '--max-colors', type=int, default=256,
                       help='Maximum number of colors (default: 256)')
    
    args = parser.parse_args()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    
    if not args.input.lower().endswith('.gif'):
        print(f"Error: Input file must be a GIF")
        sys.exit(1)
    
    # Validate frame count
    if args.frames is not None and not (1 <= args.frames <= 64):
        print("Error: Frame count must be between 1 and 64")
        sys.exit(1)
    
    # Validate FPS
    if not (1 <= args.fps <= 60):
        print("Error: FPS must be between 1 and 60")
        sys.exit(1)
    
    try:
        convert_gif(
            input_path=args.input,
            output_path=args.output,
            frames=args.frames,
            fps=args.fps,
            strategy=args.strategy,
            optimize_colors=not args.no_optimize,
            max_colors=args.max_colors
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
