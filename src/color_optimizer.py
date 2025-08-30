"""
Color Optimization Module for VRChat Sprite Sheets

Analyzes color usage across frames and creates optimized palettes to reduce file size.
"""

from typing import List, Dict, Tuple, Set
from PIL import Image
import numpy as np
from collections import Counter


class ColorOptimizer:
    """Optimizes color palettes for sprite sheets to reduce file size."""
    
    def __init__(self, max_colors: int = 256):
        """
        Initialize the color optimizer.
        
        Args:
            max_colors: Maximum number of colors in the optimized palette
        """
        self.max_colors = max_colors
    
    def analyze_colors(self, frames: List[Image.Image]) -> Dict[str, any]:
        """
        Analyze color usage across all frames.
        
        Args:
            frames: List of PIL Image objects
            
        Returns:
            Dictionary with color analysis information
        """
        all_colors = []
        color_counts = Counter()
        
        for frame in frames:
            # Convert to RGBA if not already
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            
            # Get all unique colors in the frame
            frame_colors = frame.getcolors(maxcolors=frame.size[0] * frame.size[1])
            if frame_colors:
                for count, color in frame_colors:
                    all_colors.append(color)
                    color_counts[color] += count
        
        # Calculate statistics
        unique_colors = len(color_counts)
        total_pixels = sum(color_counts.values())
        
        # Find most common colors
        most_common = color_counts.most_common(10)
        
        # Calculate color distribution
        color_distribution = {}
        for color, count in most_common:
            percentage = (count / total_pixels) * 100
            color_distribution[color] = {
                'count': count,
                'percentage': percentage
            }
        
        return {
            'unique_colors': unique_colors,
            'total_pixels': total_pixels,
            'most_common_colors': most_common,
            'color_distribution': color_distribution,
            'all_colors': list(color_counts.keys())
        }
    
    def create_optimized_palette(self, frames: List[Image.Image], target_colors: int = None) -> List[Tuple[int, int, int, int]]:
        """
        Create an optimized color palette for the frames.
        
        Args:
            frames: List of PIL Image objects
            target_colors: Target number of colors (if None, uses self.max_colors)
            
        Returns:
            List of RGBA color tuples
        """
        if target_colors is None:
            target_colors = self.max_colors
        
        # Analyze colors
        analysis = self.analyze_colors(frames)
        
        if analysis['unique_colors'] <= target_colors:
            # No optimization needed
            return analysis['all_colors']
        
        # Use k-means clustering to find optimal colors
        return self._kmeans_clustering(frames, target_colors)
    
    def _kmeans_clustering(self, frames: List[Image.Image], k: int) -> List[Tuple[int, int, int, int]]:
        """
        Use k-means clustering to find optimal color palette.
        
        Args:
            frames: List of PIL Image objects
            k: Number of colors to find
            
        Returns:
            List of RGBA color tuples
        """
        # Collect all pixel colors with sampling for large images
        all_pixels = []
        max_pixels_per_frame = 10000  # Limit pixels per frame to avoid memory issues
        
        for frame in frames:
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            pixels = list(frame.getdata())
            
            # Sample pixels if the image is too large
            if len(pixels) > max_pixels_per_frame:
                # Take a random sample of pixels
                import random
                random.seed(42)  # For reproducible results
                pixels = random.sample(pixels, max_pixels_per_frame)
            
            all_pixels.extend(pixels)
        
        if not all_pixels:
            return [(0, 0, 0, 255)]
        
        # Convert to numpy array
        pixels_array = np.array(all_pixels, dtype=np.float32)
        
        # Initialize centroids randomly
        np.random.seed(42)  # For reproducible results
        centroids = pixels_array[np.random.choice(len(pixels_array), k, replace=False)]
        
        # K-means iteration with reduced iterations for speed
        max_iterations = 50  # Reduced from 100
        tolerance = 1e-3  # Slightly relaxed tolerance
        
        try:
            for iteration in range(max_iterations):
                # Assign pixels to nearest centroid
                distances = np.sqrt(((pixels_array[:, np.newaxis, :] - centroids[np.newaxis, :, :]) ** 2).sum(axis=2))
                assignments = np.argmin(distances, axis=1)
                
                # Update centroids
                new_centroids = np.zeros_like(centroids)
                for i in range(k):
                    if np.sum(assignments == i) > 0:
                        new_centroids[i] = np.mean(pixels_array[assignments == i], axis=0)
                    else:
                        # If no pixels assigned to this centroid, keep the old one
                        new_centroids[i] = centroids[i]
                
                # Check convergence
                if np.max(np.abs(new_centroids - centroids)) < tolerance:
                    break
                
                centroids = new_centroids
        except Exception as e:
            # If k-means fails, fall back to simple color sampling
            print(f"K-means clustering failed: {e}. Using simple color sampling.")
            return self._simple_color_sampling(frames, k)
        
        # Convert centroids to integer RGBA values
        palette = []
        for centroid in centroids:
            rgba = tuple(int(round(c)) for c in centroid)
            palette.append(rgba)
        
        return palette
    
    def _simple_color_sampling(self, frames: List[Image.Image], k: int) -> List[Tuple[int, int, int, int]]:
        """
        Simple color sampling as fallback when k-means fails.
        
        Args:
            frames: List of PIL Images
            k: Number of colors in the palette
            
        Returns:
            List of RGBA color tuples
        """
        # Collect unique colors from all frames
        unique_colors = set()
        max_colors_per_frame = 5000  # Limit to avoid memory issues
        
        for frame in frames:
            if frame.mode != 'RGBA':
                frame = frame.convert('RGBA')
            pixels = list(frame.getdata())
            
            # Sample pixels if too many
            if len(pixels) > max_colors_per_frame:
                import random
                random.seed(42)
                pixels = random.sample(pixels, max_colors_per_frame)
            
            unique_colors.update(pixels)
        
        if not unique_colors:
            return [(0, 0, 0, 255)]
        
        # Convert to list and sort by frequency (approximate)
        color_list = list(unique_colors)
        
        # If we have fewer colors than requested, return all
        if len(color_list) <= k:
            return color_list
        
        # Otherwise, sample evenly across the color space
        step = len(color_list) // k
        sampled_colors = []
        for i in range(k):
            idx = i * step
            if idx < len(color_list):
                sampled_colors.append(color_list[idx])
        
        return sampled_colors
    
    def apply_palette(self, image: Image.Image, palette: List[Tuple[int, int, int, int]]) -> Image.Image:
        """
        Apply the optimized palette to an image using efficient numpy operations.
        
        Args:
            image: PIL Image to optimize
            palette: List of RGBA color tuples
            
        Returns:
            Optimized PIL Image
        """
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Convert image to numpy array for faster processing
        img_array = np.array(image)
        
        # Convert palette to numpy array
        palette_array = np.array(palette)
        
        # Reshape image to 2D array of pixels
        pixels = img_array.reshape(-1, 4)  # RGBA
        
        # Calculate distances to all palette colors efficiently
        # Only use RGB channels for distance calculation
        rgb_pixels = pixels[:, :3]
        rgb_palette = palette_array[:, :3]
        
        # Vectorized distance calculation
        distances = np.sqrt(((rgb_pixels[:, np.newaxis, :] - rgb_palette[np.newaxis, :, :]) ** 2).sum(axis=2))
        
        # Find closest palette color for each pixel
        closest_indices = np.argmin(distances, axis=1)
        
        # Replace pixels with closest palette colors
        optimized_pixels = palette_array[closest_indices]
        
        # Reshape back to image dimensions
        optimized_array = optimized_pixels.reshape(img_array.shape)
        
        # Convert back to PIL Image
        optimized_image = Image.fromarray(optimized_array.astype(np.uint8), 'RGBA')
        
        return optimized_image
    
    def optimize_sprite_sheet(self, sprite_sheet: Image.Image, target_colors: int = None) -> Image.Image:
        """
        Optimize a sprite sheet by reducing its color palette.
        
        Args:
            sprite_sheet: PIL Image of the sprite sheet
            target_colors: Target number of colors
            
        Returns:
            Optimized sprite sheet
        """
        if target_colors is None:
            target_colors = self.max_colors
        
        # Analyze current colors
        analysis = self.analyze_colors([sprite_sheet])
        
        if analysis['unique_colors'] <= target_colors:
            # No optimization needed
            return sprite_sheet
        
        # Create optimized palette
        palette = self.create_optimized_palette([sprite_sheet], target_colors)
        
        # Apply palette
        return self.apply_palette(sprite_sheet, palette)
    
    def get_optimization_stats(self, original_image: Image.Image, optimized_image: Image.Image) -> Dict[str, any]:
        """
        Get statistics about the optimization process.
        
        Args:
            original_image: Original PIL Image
            optimized_image: Optimized PIL Image
            
        Returns:
            Dictionary with optimization statistics
        """
        original_analysis = self.analyze_colors([original_image])
        optimized_analysis = self.analyze_colors([optimized_image])
        
        # Calculate file size reduction (approximate)
        original_colors = original_analysis['unique_colors']
        optimized_colors = optimized_analysis['unique_colors']
        
        # Estimate size reduction based on color depth
        if original_colors <= 256:
            original_bits = 8
        else:
            original_bits = 24  # Full RGB
        
        if optimized_colors <= 256:
            optimized_bits = 8
        else:
            optimized_bits = 24
        
        size_reduction = ((original_bits - optimized_bits) / original_bits) * 100
        
        return {
            'original_colors': original_colors,
            'optimized_colors': optimized_colors,
            'color_reduction': original_colors - optimized_colors,
            'size_reduction_percent': size_reduction,
            'original_analysis': original_analysis,
            'optimized_analysis': optimized_analysis
        }
