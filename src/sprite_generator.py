"""
Sprite Sheet Generator for VRChat

Creates VRChat-compatible sprite sheets with proper grid layouts and frame arrangements.
"""

from typing import List, Tuple, Optional, Dict, Any
from PIL import Image
import math


class VRChatSpriteGenerator:
    """Generates VRChat-compatible sprite sheets."""
    
    # VRChat sprite sheet specifications
    SPRITE_SHEET_SIZE = (1024, 1024)
    GRID_LAYOUTS = {
        4: (2, 2, 512),    # 2x2 grid, 512x512 frames
        16: (4, 4, 256),   # 4x4 grid, 256x256 frames
        64: (8, 8, 128)    # 8x8 grid, 128x128 frames
    }
    
    def __init__(self):
        """Initialize the sprite sheet generator."""
        pass
    
    def determine_grid_layout(self, frame_count: int) -> Tuple[int, int, int]:
        """
        Determine the optimal grid layout for the given frame count.
        
        Args:
            frame_count: Number of frames to include
            
        Returns:
            Tuple of (grid_width, grid_height, frame_size)
        """
        if frame_count <= 4:
            return self.GRID_LAYOUTS[4]
        elif frame_count <= 16:
            return self.GRID_LAYOUTS[16]
        else:
            return self.GRID_LAYOUTS[64]
    
    def create_sprite_sheet(self, frames: List[Image.Image], frame_count: Optional[int] = None) -> Image.Image:
        """
        Create a VRChat-compatible sprite sheet from the given frames.
        
        Args:
            frames: List of PIL Image objects
            frame_count: Number of frames to use (if None, uses all frames)
            
        Returns:
            PIL Image of the sprite sheet
        """
        if not frames:
            raise ValueError("No frames provided")
        
        # Use all frames if frame_count not specified
        if frame_count is None:
            frame_count = len(frames)
        
        # Limit frame count to available frames
        frame_count = min(frame_count, len(frames))
        
        # Determine grid layout
        grid_width, grid_height, frame_size = self.determine_grid_layout(frame_count)
        
        # Create sprite sheet canvas
        sprite_sheet = Image.new('RGBA', self.SPRITE_SHEET_SIZE, (0, 0, 0, 0))
        
        # Place frames in grid (left to right, top to bottom)
        for i in range(frame_count):
            # Calculate grid position
            row = i // grid_width
            col = i % grid_width
            
            # Calculate pixel position
            x = col * frame_size
            y = row * frame_size
            
            # Get frame and resize to target size
            frame = frames[i]
            resized_frame = self._resize_frame(frame, (frame_size, frame_size))
            
            # Paste frame onto sprite sheet
            sprite_sheet.paste(resized_frame, (x, y), resized_frame)
        
        return sprite_sheet
    
    def _resize_frame(self, frame: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Resize a frame to the target size while maintaining aspect ratio.
        
        Args:
            frame: PIL Image to resize
            target_size: Target (width, height)
            
        Returns:
            Resized PIL Image
        """
        # Convert to RGBA if not already
        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')
        
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
        
        return normalized_frame
    
    def get_sprite_sheet_info(self, frame_count: int) -> Dict[str, Any]:
        """
        Get information about the sprite sheet configuration for a given frame count.
        
        Args:
            frame_count: Number of frames
            
        Returns:
            Dictionary with sprite sheet information
        """
        grid_width, grid_height, frame_size = self.determine_grid_layout(frame_count)
        total_cells = grid_width * grid_height
        unused_cells = total_cells - frame_count
        
        return {
            'frame_count': frame_count,
            'grid_width': grid_width,
            'grid_height': grid_height,
            'frame_size': frame_size,
            'total_cells': total_cells,
            'unused_cells': unused_cells,
            'sprite_sheet_size': self.SPRITE_SHEET_SIZE,
            'layout_name': f"{grid_width}x{grid_height}"
        }
    
    def validate_frame_count(self, frame_count: int) -> bool:
        """
        Validate if the frame count is within VRChat limits.
        
        Args:
            frame_count: Number of frames
            
        Returns:
            True if valid, False otherwise
        """
        return 1 <= frame_count <= 64
    
    def get_optimization_suggestions(self, original_frame_count: int) -> List[Dict[str, Any]]:
        """
        Get suggestions for optimizing frame count to fit VRChat requirements.
        
        Args:
            original_frame_count: Original number of frames
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        if original_frame_count <= 64:
            # Already within limits
            return suggestions
        
        # Calculate reduction factors
        reduction_factors = [2, 3, 4, 5, 6, 8, 10]
        
        for factor in reduction_factors:
            reduced_count = original_frame_count // factor
            if reduced_count <= 64 and reduced_count > 0:
                suggestions.append({
                    'reduction_factor': factor,
                    'reduced_frames': reduced_count,
                    'description': f"Remove every {factor}th frame",
                    'grid_layout': self.determine_grid_layout(reduced_count)
                })
        
        # Sort by reduced frame count (prefer higher counts)
        suggestions.sort(key=lambda x: x['reduced_frames'], reverse=True)
        
        return suggestions
