"""
Filename Parser for VRChat Sprite Sheets

Extracts frame count and FPS information from filenames for easier sharing.
"""

import re
import os
from typing import Dict, Optional, Tuple, List


class FilenameParser:
    """Parses filenames to extract VRChat sprite sheet parameters."""
    
    def __init__(self):
        """Initialize the filename parser."""
        # Regex patterns for extracting parameters
        self.frame_pattern = r'(\d+)frames?'
        self.fps_pattern = r'(\d+)fps'
        self.valid_extensions = {'.png', '.jpg', '.jpeg', '.gif'}
    
    def parse_filename(self, filename: str) -> Dict[str, Optional[int]]:
        """
        Parse a filename to extract frame count and FPS.
        
        Args:
            filename: Filename to parse (e.g., "VRRatEmoji_14frames_20fps.png")
            
        Returns:
            Dictionary with 'frames' and 'fps' values (None if not found)
        """
        # Remove extension for parsing
        name_without_ext = os.path.splitext(filename)[0]
        
        # Extract frame count
        frame_match = re.search(self.frame_pattern, name_without_ext, re.IGNORECASE)
        frames = int(frame_match.group(1)) if frame_match else None
        
        # Extract FPS
        fps_match = re.search(self.fps_pattern, name_without_ext, re.IGNORECASE)
        fps = int(fps_match.group(1)) if fps_match else None
        
        return {
            'frames': frames,
            'fps': fps
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
    
    def validate_fps(self, fps: int) -> bool:
        """
        Validate if the FPS is reasonable.
        
        Args:
            fps: Frames per second
            
        Returns:
            True if valid, False otherwise
        """
        return 1 <= fps <= 60
    
    def generate_filename(self, base_name: str, frames: int, fps: int, extension: str = '.png') -> str:
        """
        Generate a filename with embedded parameters.
        
        Args:
            base_name: Base name for the file
            frames: Number of frames
            fps: Frames per second
            extension: File extension (default: .png)
            
        Returns:
            Generated filename
        """
        # Clean base name (remove existing parameters)
        clean_name = self._clean_base_name(base_name)
        
        # Generate filename
        filename = f"{clean_name}_{frames}frames_{fps}fps{extension}"
        
        return filename
    
    def _clean_base_name(self, base_name: str) -> str:
        """
        Clean base name by removing existing frame/fps parameters.
        
        Args:
            base_name: Base name to clean
            
        Returns:
            Cleaned base name
        """
        # Remove frame and fps patterns
        cleaned = re.sub(self.frame_pattern, '', base_name, flags=re.IGNORECASE)
        cleaned = re.sub(self.fps_pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Remove extra underscores and spaces
        cleaned = re.sub(r'[_\s]+', '_', cleaned)
        cleaned = cleaned.strip('_')
        
        return cleaned
    
    def extract_base_name(self, filename: str) -> str:
        """
        Extract the base name from a filename with parameters.
        
        Args:
            filename: Filename to extract base name from
            
        Returns:
            Base name without parameters
        """
        name_without_ext = os.path.splitext(filename)[0]
        return self._clean_base_name(name_without_ext)
    
    def get_suggested_filename(self, original_filename: str, frames: int, fps: int) -> str:
        """
        Get a suggested filename with embedded parameters.
        
        Args:
            original_filename: Original filename
            frames: Number of frames
            fps: Frames per second
            
        Returns:
            Suggested filename
        """
        # Extract base name and extension
        base_name = self.extract_base_name(original_filename)
        _, extension = os.path.splitext(original_filename)
        
        # Use .png if no valid extension
        if extension.lower() not in self.valid_extensions:
            extension = '.png'
        
        return self.generate_filename(base_name, frames, fps, extension)
    
    def parse_file_path(self, file_path: str) -> Dict[str, any]:
        """
        Parse a complete file path to extract information.
        
        Args:
            file_path: Complete file path
            
        Returns:
            Dictionary with parsed information
        """
        filename = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        
        parsed = self.parse_filename(filename)
        
        return {
            'filename': filename,
            'directory': directory,
            'full_path': file_path,
            'frames': parsed['frames'],
            'fps': parsed['fps'],
            'base_name': self.extract_base_name(filename),
            'extension': os.path.splitext(filename)[1]
        }
    
    def is_valid_filename_format(self, filename: str) -> bool:
        """
        Check if filename follows the expected format.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if format is valid, False otherwise
        """
        parsed = self.parse_filename(filename)
        return parsed['frames'] is not None or parsed['fps'] is not None
    
    def get_filename_examples(self) -> List[str]:
        """
        Get example filenames for reference.
        
        Returns:
            List of example filenames
        """
        return [
            "VRRatEmoji_14frames_20fps.png",
            "MyAnimation_8frames_30fps.png",
            "Dance_16frames_15fps.png",
            "Wave_4frames_10fps.png",
            "CustomName_64frames_25fps.png"
        ]
