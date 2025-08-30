"""
GIF Processing Module for VRChat Sprite Sheet Generator

Handles loading GIF files, extracting frames, and managing frame timing information.
"""

import os
from typing import List, Tuple, Optional, Dict, Any
from PIL import Image, ImageSequence
import imageio
import numpy as np


class GIFProcessor:
    """Handles GIF file processing and frame extraction."""
    
    def __init__(self, gif_path: str):
        """
        Initialize GIF processor with a GIF file path.
        
        Args:
            gif_path: Path to the GIF file to process
        """
        self.gif_path = gif_path
        self.frames = []
        self.frame_durations = []
        self.original_dimensions = None
        self.total_frames = 0
        self.loop_count = 0
        
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        
        self._load_gif()
    
    def _load_gif(self):
        """Load the GIF and extract frame information."""
        try:
            # Load with PIL to preserve transparency properly
            with Image.open(self.gif_path) as gif:
                # Get loop count from imageio (PIL doesn't always preserve this)
                try:
                    gif_reader = imageio.get_reader(self.gif_path)
                    self.loop_count = gif_reader.get_meta_data().get('loop', 0)
                    gif_reader.close()
                except:
                    self.loop_count = 0
                
                # Extract frames using PIL's ImageSequence
                for frame in ImageSequence.Iterator(gif):
                    # Ensure frame has proper transparency
                    if frame.mode == 'P':
                        # Convert palette mode to RGBA to preserve transparency
                        frame = frame.convert('RGBA')
                    elif frame.mode != 'RGBA':
                        # Convert other modes to RGBA
                        frame = frame.convert('RGBA')
                    
                    # Ensure the frame has a proper alpha channel
                    if frame.mode == 'RGBA':
                        # Check if alpha channel is all opaque (255)
                        alpha = frame.split()[-1]
                        if alpha.getextrema() == (255, 255):
                            # All pixels are opaque, convert to RGB for better compatibility
                            frame = frame.convert('RGB')
                    
                    self.frames.append(frame.copy())
                    
                    # Get frame duration (default to 100ms if not available)
                    try:
                        duration = frame.info.get('duration', 100)
                        self.frame_durations.append(duration)
                    except:
                        self.frame_durations.append(100)
            
            self.total_frames = len(self.frames)
            
            if self.total_frames == 0:
                raise ValueError("No frames found in GIF")
            
            # Get original dimensions from first frame
            self.original_dimensions = self.frames[0].size
            
        except Exception as e:
            raise ValueError(f"Failed to load GIF: {str(e)}")
    
    def get_frame_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded GIF.
        
        Returns:
            Dictionary containing GIF information
        """
        return {
            'total_frames': self.total_frames,
            'original_dimensions': self.original_dimensions,
            'loop_count': self.loop_count,
            'frame_durations': self.frame_durations,
            'average_duration': sum(self.frame_durations) / len(self.frame_durations) if self.frame_durations else 0
        }
    
    def get_frames(self) -> List[Image.Image]:
        """
        Get all frames from the GIF.
        
        Returns:
            List of PIL Image objects
        """
        return self.frames.copy()
    
    def reduce_frames(self, target_count: int, strategy: str = 'uniform') -> List[Image.Image]:
        """
        Reduce the number of frames to meet VRChat requirements.
        
        Args:
            target_count: Target number of frames
            strategy: Reduction strategy ('uniform', 'keep_ends', 'smart')
        
        Returns:
            List of reduced frames
        """
        if self.total_frames <= target_count:
            return self.frames.copy()
        
        if strategy == 'keep_ends':
            return self._reduce_keep_ends(target_count)
        elif strategy == 'smart':
            return self._reduce_smart(target_count)
        else:  # uniform
            return self._reduce_uniform(target_count)
    
    def _reduce_keep_ends(self, target_count: int) -> List[Image.Image]:
        """Reduce frames while keeping first and last frame to preserve loops."""
        if target_count < 2:
            return self.frames[:target_count]
        
        # Always keep first and last frame
        kept_frames = [self.frames[0]]
        
        # Calculate step size for remaining frames
        remaining_frames = target_count - 2
        if remaining_frames > 0:
            step = (self.total_frames - 2) / remaining_frames
            for i in range(1, remaining_frames + 1):
                frame_index = int(i * step)
                if frame_index < self.total_frames - 1:  # Don't include last frame yet
                    kept_frames.append(self.frames[frame_index])
        
        kept_frames.append(self.frames[-1])
        return kept_frames
    
    def _reduce_uniform(self, target_count: int) -> List[Image.Image]:
        """Reduce frames uniformly across the sequence."""
        if target_count >= self.total_frames:
            return self.frames.copy()
        
        step = self.total_frames / target_count
        reduced_frames = []
        
        for i in range(target_count):
            frame_index = int(i * step)
            if frame_index < self.total_frames:
                reduced_frames.append(self.frames[frame_index])
        
        return reduced_frames
    
    def _reduce_smart(self, target_count: int) -> List[Image.Image]:
        """Smart reduction that tries to preserve key frames."""
        # For now, use keep_ends strategy as it's most effective for loops
        return self._reduce_keep_ends(target_count)
    
    def normalize_frames(self, target_size: Tuple[int, int]) -> List[Image.Image]:
        """
        Normalize all frames to the target size while maintaining aspect ratio.
        
        Args:
            target_size: Target (width, height) for all frames
        
        Returns:
            List of normalized frames
        """
        normalized_frames = []
        
        for frame in self.frames:
            # Calculate scaling to fit within target size while maintaining aspect ratio
            frame_ratio = frame.size[0] / frame.size[1]
            target_ratio = target_size[0] / target_size[1]
            
            if frame_ratio > target_ratio:
                # Frame is wider than target
                new_width = target_size[0]
                new_height = int(target_size[0] / frame_ratio)
            else:
                # Frame is taller than target
                new_height = target_size[1]
                new_width = int(target_size[1] * frame_ratio)
            
            # Resize frame
            resized_frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create new image with target size and transparent background
            normalized_frame = Image.new('RGBA', target_size, (0, 0, 0, 0))
            
            # Center the resized frame
            x_offset = (target_size[0] - new_width) // 2
            y_offset = (target_size[1] - new_height) // 2
            normalized_frame.paste(resized_frame, (x_offset, y_offset))
            
            normalized_frames.append(normalized_frame)
        
        return normalized_frames
