#!/usr/bin/env python3
"""
Test script for VRChat GIF Maker

Tests core functionality without requiring a GUI.
"""

import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.sprite_generator import VRChatSpriteGenerator
from src.color_optimizer import ColorOptimizer
from src.utils.filename_parser import FilenameParser
from src.utils.frame_reducer import FrameReducer
from PIL import Image
import numpy as np


def test_sprite_generator():
    """Test the sprite sheet generator."""
    print("Testing Sprite Sheet Generator...")
    
    generator = VRChatSpriteGenerator()
    
    # Test grid layout determination
    assert generator.determine_grid_layout(2) == (2, 2, 512)
    assert generator.determine_grid_layout(8) == (4, 4, 256)
    assert generator.determine_grid_layout(32) == (8, 8, 128)
    
    # Test frame count validation
    assert generator.validate_frame_count(1) == True
    assert generator.validate_frame_count(64) == True
    assert generator.validate_frame_count(65) == False
    assert generator.validate_frame_count(0) == False
    
    print("[OK] Sprite Sheet Generator tests passed")


def test_filename_parser():
    """Test the filename parser."""
    print("Testing Filename Parser...")
    
    parser = FilenameParser()
    
    # Test parsing
    result = parser.parse_filename("VRRatEmoji_14frames_20fps.png")
    assert result['frames'] == 14
    assert result['fps'] == 20
    
    result = parser.parse_filename("MyAnimation_8frames_30fps.png")
    assert result['frames'] == 8
    assert result['fps'] == 30
    
    # Test validation
    assert parser.validate_frame_count(32) == True
    assert parser.validate_frame_count(65) == False
    assert parser.validate_fps(25) == True
    assert parser.validate_fps(65) == False
    
    # Test filename generation
    filename = parser.generate_filename("Test", 16, 15)
    assert "16frames" in filename
    assert "15fps" in filename
    
    print("[OK] Filename Parser tests passed")


def test_frame_reducer():
    """Test the frame reducer."""
    print("Testing Frame Reducer...")
    
    reducer = FrameReducer()
    
    # Create test frames (simple colored squares)
    frames = []
    for i in range(10):
        # Create a simple colored square
        color = (i * 25, 255 - i * 25, 128, 255)
        frame = Image.new('RGBA', (100, 100), color)
        frames.append(frame)
    
    # Test reduction
    reduced = reducer.reduce_frames(frames, 5, 'keep_ends')
    assert len(reduced) == 5
    assert reduced[0] == frames[0]  # First frame preserved
    assert reduced[-1] == frames[-1]  # Last frame preserved
    
    reduced = reducer.reduce_frames(frames, 3, 'uniform')
    assert len(reduced) == 3
    
    print("[OK] Frame Reducer tests passed")


def test_color_optimizer():
    """Test the color optimizer."""
    print("Testing Color Optimizer...")
    
    optimizer = ColorOptimizer()
    
    # Create test image with many colors
    test_image = Image.new('RGBA', (100, 100))
    pixels = []
    for i in range(10000):
        r = i % 256
        g = (i * 2) % 256
        b = (i * 3) % 256
        pixels.append((r, g, b, 255))
    
    test_image.putdata(pixels)
    
    # Test color analysis
    analysis = optimizer.analyze_colors([test_image])
    assert analysis['unique_colors'] > 0
    assert analysis['total_pixels'] == 10000
    
    # Test optimization
    optimized = optimizer.optimize_sprite_sheet(test_image, 64)
    optimized_analysis = optimizer.analyze_colors([optimized])
    assert optimized_analysis['unique_colors'] <= 64
    
    print("[OK] Color Optimizer tests passed")


def test_integration():
    """Test integration of components."""
    print("Testing Integration...")
    
    # Create a simple test sprite sheet
    generator = VRChatSpriteGenerator()
    optimizer = ColorOptimizer()
    
    # Create test frames
    frames = []
    for i in range(4):
        color = (i * 64, 255 - i * 64, 128, 255)
        frame = Image.new('RGBA', (200, 200), color)
        frames.append(frame)
    
    # Generate sprite sheet
    sprite_sheet = generator.create_sprite_sheet(frames, 4)
    assert sprite_sheet.size == (1024, 1024)
    
    # Optimize colors
    optimized = optimizer.optimize_sprite_sheet(sprite_sheet, 16)
    
    # Get stats
    stats = optimizer.get_optimization_stats(sprite_sheet, optimized)
    assert stats['original_colors'] >= stats['optimized_colors']
    
    print("[OK] Integration tests passed")


def main():
    """Run all tests."""
    print("Running VRChat GIF Maker Tests...")
    print("=" * 50)
    
    try:
        test_sprite_generator()
        test_filename_parser()
        test_frame_reducer()
        test_color_optimizer()
        test_integration()
        
        print("=" * 50)
        print("All tests passed! The application is working correctly.")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
