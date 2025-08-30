"""
Frame Reducer Utility for VRChat Sprite Sheets

Handles different strategies for reducing frame counts to fit VRChat requirements.
"""

from typing import List, Dict, Any
from PIL import Image


class FrameReducer:
    """Handles frame reduction strategies for VRChat sprite sheets."""
    
    def __init__(self):
        """Initialize the frame reducer."""
        self.strategies = {
            'keep_ends': self._reduce_keep_ends,
            'uniform': self._reduce_uniform,
            'smart': self._reduce_smart,
            'every_nth': self._reduce_every_nth
        }
    
    def reduce_frames(self, frames: List[Image.Image], target_count: int, strategy: str = 'keep_ends') -> List[Image.Image]:
        """
        Reduce frames using the specified strategy.
        
        Args:
            frames: List of PIL Image objects
            target_count: Target number of frames
            strategy: Reduction strategy to use
            
        Returns:
            List of reduced frames
        """
        if len(frames) <= target_count:
            return frames.copy()
        
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        return self.strategies[strategy](frames, target_count)
    
    def _reduce_keep_ends(self, frames: List[Image.Image], target_count: int) -> List[Image.Image]:
        """
        Reduce frames while keeping first and last frame to preserve loops.
        
        Args:
            frames: List of PIL Image objects
            target_count: Target number of frames
            
        Returns:
            List of reduced frames
        """
        if target_count < 2:
            return frames[:target_count]
        
        # Always keep first and last frame
        kept_frames = [frames[0]]
        
        # Calculate step size for remaining frames
        remaining_frames = target_count - 2
        if remaining_frames > 0:
            step = (len(frames) - 2) / remaining_frames
            for i in range(1, remaining_frames + 1):
                frame_index = int(i * step)
                if frame_index < len(frames) - 1:  # Don't include last frame yet
                    kept_frames.append(frames[frame_index])
        
        kept_frames.append(frames[-1])
        return kept_frames
    
    def _reduce_uniform(self, frames: List[Image.Image], target_count: int) -> List[Image.Image]:
        """
        Reduce frames uniformly across the sequence.
        
        Args:
            frames: List of PIL Image objects
            target_count: Target number of frames
            
        Returns:
            List of reduced frames
        """
        if target_count >= len(frames):
            return frames.copy()
        
        step = len(frames) / target_count
        reduced_frames = []
        
        for i in range(target_count):
            frame_index = int(i * step)
            if frame_index < len(frames):
                reduced_frames.append(frames[frame_index])
        
        return reduced_frames
    
    def _reduce_smart(self, frames: List[Image.Image], target_count: int) -> List[Image.Image]:
        """
        Smart reduction that tries to preserve key frames based on visual differences.
        
        Args:
            frames: List of PIL Image objects
            target_count: Target number of frames
            
        Returns:
            List of reduced frames
        """
        if target_count >= len(frames):
            return frames.copy()
        
        # For now, use keep_ends strategy as it's most effective for loops
        # In the future, this could analyze frame differences to keep important frames
        return self._reduce_keep_ends(frames, target_count)
    
    def _reduce_every_nth(self, frames: List[Image.Image], target_count: int) -> List[Image.Image]:
        """
        Reduce frames by taking every nth frame.
        
        Args:
            frames: List of PIL Image objects
            target_count: Target number of frames
            
        Returns:
            List of reduced frames
        """
        if target_count >= len(frames):
            return frames.copy()
        
        # Calculate nth value
        nth = len(frames) // target_count
        if nth < 1:
            nth = 1
        
        reduced_frames = []
        for i in range(0, len(frames), nth):
            if len(reduced_frames) >= target_count:
                break
            reduced_frames.append(frames[i])
        
        return reduced_frames
    
    def get_reduction_suggestions(self, frame_count: int) -> List[Dict[str, Any]]:
        """
        Get suggestions for reducing frame count to fit VRChat requirements.
        
        Args:
            frame_count: Original number of frames
            
        Returns:
            List of reduction suggestions
        """
        suggestions = []
        
        if frame_count <= 64:
            # Already within limits
            return suggestions
        
        # Calculate reduction factors
        reduction_factors = [2, 3, 4, 5, 6, 8, 10]
        
        for factor in reduction_factors:
            reduced_count = frame_count // factor
            if reduced_count <= 64 and reduced_count > 0:
                suggestions.append({
                    'reduction_factor': factor,
                    'reduced_frames': reduced_count,
                    'description': f"Remove every {factor}th frame",
                    'strategy': 'every_nth',
                    'factor': factor
                })
        
        # Add keep_ends strategy suggestions
        for target in [4, 16, 64]:
            if frame_count > target:
                suggestions.append({
                    'reduction_factor': None,
                    'reduced_frames': target,
                    'description': f"Reduce to {target} frames (keep first/last)",
                    'strategy': 'keep_ends'
                })
        
        # Sort by reduced frame count (prefer higher counts)
        suggestions.sort(key=lambda x: x['reduced_frames'], reverse=True)
        
        return suggestions
    
    def analyze_frame_differences(self, frames: List[Image.Image]) -> List[float]:
        """
        Analyze differences between consecutive frames.
        
        Args:
            frames: List of PIL Image objects
            
        Returns:
            List of difference scores between consecutive frames
        """
        differences = []
        
        for i in range(1, len(frames)):
            # Convert frames to grayscale for comparison
            frame1 = frames[i-1].convert('L')
            frame2 = frames[i].convert('L')
            
            # Calculate mean absolute difference
            diff = sum(abs(a - b) for a, b in zip(frame1.getdata(), frame2.getdata()))
            avg_diff = diff / (frame1.size[0] * frame1.size[1])
            
            differences.append(avg_diff)
        
        return differences
    
    def get_key_frames(self, frames: List[Image.Image], target_count: int) -> List[Image.Image]:
        """
        Get key frames based on visual differences.
        
        Args:
            frames: List of PIL Image objects
            target_count: Target number of frames
            
        Returns:
            List of key frames
        """
        if len(frames) <= target_count:
            return frames.copy()
        
        # Analyze frame differences
        differences = self.analyze_frame_differences(frames)
        
        # Find frames with high differences (key frames)
        threshold = sum(differences) / len(differences) * 1.5
        
        key_frames = [frames[0]]  # Always include first frame
        
        for i, diff in enumerate(differences):
            if diff > threshold and len(key_frames) < target_count - 1:
                key_frames.append(frames[i + 1])
        
        # Always include last frame if we have room
        if len(key_frames) < target_count:
            key_frames.append(frames[-1])
        
        # If we still have room, add more frames
        while len(key_frames) < target_count and len(key_frames) < len(frames):
            # Add frames that weren't selected yet
            for frame in frames:
                if frame not in key_frames and len(key_frames) < target_count:
                    key_frames.append(frame)
                    break
        
        return key_frames[:target_count]
