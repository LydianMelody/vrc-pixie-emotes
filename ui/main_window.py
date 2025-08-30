"""
Main GUI Window for VRChat GIF Maker

Provides a user-friendly interface with drag-and-drop functionality and preview capabilities.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
from typing import Optional, Dict, Any
from PIL import Image, ImageTk

from src.gif_processor import GIFProcessor
from src.sprite_generator import VRChatSpriteGenerator
from src.color_optimizer import ColorOptimizer
from src.utils.filename_parser import FilenameParser
from src.utils.frame_reducer import FrameReducer


class MainWindow:
    """Main application window for VRChat GIF Maker."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the main window.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("PIXIE — Pixel Image eXporter for Instant Emotes by LydianMelody")
        self.root.geometry("1200x1070")
        self.root.minsize(1000, 600)
        
        # Initialize components
        self.gif_processor = None
        self.sprite_generator = VRChatSpriteGenerator()
        self.color_optimizer = ColorOptimizer()
        self.filename_parser = FilenameParser()
        self.frame_reducer = FrameReducer()
        
        # State variables
        self.current_gif_path = None
        self.current_frames = []
        self.current_sprite_sheet = None
        self.preview_images = []
        
        self._setup_ui()
        self._setup_drag_drop()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Create main frames
        self._create_sidebar()
        self._create_main_area()
        self._create_status_bar()
    
    def _create_sidebar(self):
        """Create the sidebar with controls."""
        sidebar = ttk.Frame(self.root, padding="10")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Logo
        try:
            logo_path = Path(__file__).parent / "PixieLogo.png"
            if logo_path.exists():
                from PIL import Image, ImageTk
                # Load and resize logo
                logo_img = Image.open(logo_path)
                # Resize to fit sidebar width (around 250px wide)
                logo_width = 250
                logo_height = int(logo_width * logo_img.height / logo_img.width)
                logo_img = logo_img.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                # Create label with logo
                logo_label = ttk.Label(sidebar, image=logo_photo)
                logo_label.image = logo_photo  # Keep a reference
                logo_label.pack(pady=(10, 5))
                
                # Subtitle
                subtitle_label = ttk.Label(sidebar, text="Pixel Image eXporter for Instant Emotes", font=("Arial", 10))
                subtitle_label.pack(pady=(0, 5))
                
                # Author
                author_label = ttk.Label(sidebar, text="by LydianMelody", font=("Arial", 9, "italic"))
                author_label.pack(pady=(0, 20))
            else:
                # Fallback to text if logo not found
                title_label = ttk.Label(sidebar, text="PIXIE", font=("Arial", 20, "bold"))
                title_label.pack(pady=(10, 5))
                
                subtitle_label = ttk.Label(sidebar, text="Pixel Image eXporter for Instant Emotes", font=("Arial", 10))
                subtitle_label.pack(pady=(0, 5))
                
                author_label = ttk.Label(sidebar, text="by LydianMelody", font=("Arial", 9, "italic"))
                author_label.pack(pady=(0, 20))
        except Exception as e:
            # Fallback to text if logo loading fails
            title_label = ttk.Label(sidebar, text="PIXIE", font=("Arial", 20, "bold"))
            title_label.pack(pady=(10, 5))
            
            subtitle_label = ttk.Label(sidebar, text="Pixel Image eXporter for Instant Emotes", font=("Arial", 10))
            subtitle_label.pack(pady=(0, 5))
            
            author_label = ttk.Label(sidebar, text="by LydianMelody", font=("Arial", 9, "italic"))
            author_label.pack(pady=(0, 20))
        
        # File selection
        file_frame = ttk.LabelFrame(sidebar, text="File Selection", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="No file selected", wraplength=200)
        self.file_label.pack(pady=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse GIF", command=self._browse_file)
        browse_btn.pack(fill="x")
        
        # GIF Information
        self.info_frame = ttk.LabelFrame(sidebar, text="GIF Information", padding="10")
        self.info_frame.pack(fill="x", pady=(0, 10))
        
        self.info_text = tk.Text(self.info_frame, height=8, width=30, wrap="word")
        self.info_text.pack(fill="both", expand=True)
        
        # Settings
        settings_frame = ttk.LabelFrame(sidebar, text="Settings", padding="10")
        settings_frame.pack(fill="x", pady=(0, 10))
        
        # Frame count
        ttk.Label(settings_frame, text="Frame Count:").pack(anchor="w")
        self.frame_count_var = tk.StringVar(value="All")
        self.frame_count_combo = ttk.Combobox(settings_frame, textvariable=self.frame_count_var, state="readonly")
        self.frame_count_combo.pack(fill="x", pady=(0, 10))
        
        # FPS
        ttk.Label(settings_frame, text="FPS:").pack(anchor="w")
        self.fps_var = tk.StringVar(value="10")
        fps_entry = ttk.Entry(settings_frame, textvariable=self.fps_var)
        fps_entry.pack(fill="x", pady=(0, 10))
        
        # Frame reduction strategy
        ttk.Label(settings_frame, text="Reduction Strategy:").pack(anchor="w")
        self.strategy_var = tk.StringVar(value="none")
        strategy_combo = ttk.Combobox(settings_frame, textvariable=self.strategy_var, 
                                    values=["none", "keep_ends", "uniform", "smart", "every_nth"], 
                                    state="readonly")
        strategy_combo.pack(fill="x", pady=(0, 10))
        
        # Color optimization
        self.optimize_colors_var = tk.BooleanVar(value=True)
        optimize_check = ttk.Checkbutton(settings_frame, text="Optimize Colors", 
                                       variable=self.optimize_colors_var)
        optimize_check.pack(anchor="w", pady=(0, 10))
        
        # Max colors
        ttk.Label(settings_frame, text="Max Colors:").pack(anchor="w")
        self.max_colors_var = tk.StringVar(value="256")
        max_colors_entry = ttk.Entry(settings_frame, textvariable=self.max_colors_var)
        max_colors_entry.pack(fill="x", pady=(0, 10))
        
        # Generate button
        self.generate_btn = ttk.Button(settings_frame, text="Generate Sprite Sheet", 
                                     command=self._generate_sprite_sheet, state="disabled")
        self.generate_btn.pack(fill="x", pady=(10, 0))
        
        # Save button
        self.save_btn = ttk.Button(settings_frame, text="Save Sprite Sheet", 
                                 command=self._save_sprite_sheet, state="disabled")
        self.save_btn.pack(fill="x", pady=(5, 0))
    
    def _create_main_area(self):
        """Create the main area with preview."""
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        # Original GIF tab
        self._create_gif_tab()
        
        # Sprite Sheet tab
        self._create_sprite_tab()
        
        # Help & Info tab
        self._create_help_tab()
    
    def _create_gif_tab(self):
        """Create the GIF preview tab."""
        gif_frame = ttk.Frame(self.notebook)
        self.notebook.add(gif_frame, text="Original GIF")
        
        # GIF preview
        self.gif_canvas = tk.Canvas(gif_frame, bg="white")
        self.gif_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame navigation
        nav_frame = ttk.Frame(gif_frame)
        nav_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.frame_var = tk.IntVar(value=0)
        self.frame_scale = ttk.Scale(nav_frame, from_=0, to=0, variable=self.frame_var, 
                                    orient="horizontal", command=self._update_gif_preview)
        self.frame_scale.pack(fill="x", side="left", expand=True)
        
        self.frame_label = ttk.Label(nav_frame, text="Frame 0/0")
        self.frame_label.pack(side="right", padx=(10, 0))
    
    def _create_sprite_tab(self):
        """Create the sprite sheet preview tab."""
        sprite_frame = ttk.Frame(self.notebook)
        self.notebook.add(sprite_frame, text="Sprite Sheet")
        
        # Sprite sheet preview
        self.sprite_canvas = tk.Canvas(sprite_frame, bg="white")
        self.sprite_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sprite sheet info
        info_frame = ttk.Frame(sprite_frame)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.sprite_info_text = tk.Text(info_frame, height=6, wrap="word")
        self.sprite_info_text.pack(fill="both", expand=True)
    
    def _create_help_tab(self):
        """Create the help and info tab."""
        help_frame = ttk.Frame(self.notebook)
        self.notebook.add(help_frame, text="Help & Info")
        
        # Help content
        content_frame = ttk.Frame(help_frame, padding="20")
        content_frame.pack(fill="both", expand=True)
        
        # VRChat specifications
        specs_frame = ttk.LabelFrame(content_frame, text="VRChat Specifications", padding="10")
        specs_frame.pack(fill="x", pady=(0, 20))
        
        specs_text = """
VRChat Sprite Sheet Requirements:

• Size: 1024x1024 pixels
• Grid layouts:
  - 2x2 (512x512 frames) for up to 4 frames
  - 4x4 (256x256 frames) for up to 16 frames  
  - 8x8 (128x128 frames) for up to 64 frames

• Frames are arranged left-to-right, then top-to-bottom
• Unused frames in the grid are ignored
• Filename format: "Name_14frames_20fps.png"
        """
        
        specs_label = ttk.Label(specs_frame, text=specs_text, justify="left")
        specs_label.pack(anchor="w")
        
        # Optimization options
        opt_frame = ttk.LabelFrame(content_frame, text="Optimization Options", padding="10")
        opt_frame.pack(fill="x", pady=(0, 20))
        
        opt_text = """
Frame Reduction Strategies:

• keep_ends: Preserves first and last frame (best for loops)
• uniform: Reduces frames evenly across sequence
• smart: Analyzes frame differences to keep key frames
• every_nth: Takes every nth frame (e.g., every 2nd, 3rd frame)

Color Optimization:

• Reduces color palette to specified maximum
• Uses k-means clustering for optimal color selection
• Maintains visual quality while reducing file size
        """
        
        opt_label = ttk.Label(opt_frame, text=opt_text, justify="left")
        opt_label.pack(anchor="w")
    
    def _create_status_bar(self):
        """Create the status bar."""
        self.status_bar = ttk.Label(self.root, text="Ready", relief="sunken")
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
    
    def _setup_drag_drop(self):
        """Set up drag and drop functionality."""
        # Try to setup drag and drop, but don't fail if not available
        try:
            # Check if drag and drop is available
            if hasattr(self.root, 'drop_target_register'):
                self.root.drop_target_register("DND_Files")
                self.root.dnd_bind('<<Drop>>', self._on_drop)
            else:
                print("Drag and drop not available - using file browser only")
        except Exception as e:
            print(f"Drag and drop setup failed: {e}")
            print("Using file browser only")
    
    def _on_drop(self, event):
        """Handle file drop events."""
        files = event.data
        if files:
            file_path = files[0]
            if file_path.lower().endswith('.gif'):
                self._load_gif(file_path)
    
    def _browse_file(self):
        """Browse for a GIF file."""
        file_path = filedialog.askopenfilename(
            title="Select GIF File",
            filetypes=[("GIF files", "*.gif"), ("All files", "*.*")]
        )
        if file_path:
            self._load_gif(file_path)
    
    def _load_gif(self, file_path: str):
        """Load a GIF file and update the interface."""
        try:
            self.status_bar.config(text="Loading GIF...")
            self.root.update()
            
            # Load GIF
            self.gif_processor = GIFProcessor(file_path)
            self.current_gif_path = file_path
            self.current_frames = self.gif_processor.get_frames()
            
            # Update file label
            filename = os.path.basename(file_path)
            self.file_label.config(text=filename)
            
            # Parse filename for default values
            parsed = self.filename_parser.parse_filename(filename)
            if parsed['frames']:
                self.frame_count_var.set(str(parsed['frames']))
            if parsed['fps']:
                self.fps_var.set(str(parsed['fps']))
            
            # Update GIF information
            self._update_gif_info()
            
            # Update frame navigation
            self._update_frame_navigation()
            
            # Enable generate button
            self.generate_btn.config(state="normal")
            
            self.status_bar.config(text="GIF loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {str(e)}")
            self.status_bar.config(text="Error loading GIF")
    
    def _update_gif_info(self):
        """Update the GIF information display."""
        if not self.gif_processor:
            return
        
        info = self.gif_processor.get_frame_info()
        
        info_text = f"""Total Frames: {info['total_frames']}
Original Size: {info['original_dimensions'][0]}x{info['original_dimensions'][1]}
Loop Count: {info['loop_count'] if info['loop_count'] > 0 else 'Infinite'}
Average Duration: {info['average_duration']:.1f}ms

Frame Durations: {', '.join(map(str, info['frame_durations'][:5]))}{'...' if len(info['frame_durations']) > 5 else ''}"""
        
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        
        # Update frame count options
        frame_counts = list(range(1, min(info['total_frames'] + 1, 65)))
        frame_counts.insert(0, info['total_frames'])
        
        # Update combobox values
        self.frame_count_combo['values'] = frame_counts
        if self.frame_count_var.get() not in map(str, frame_counts):
            self.frame_count_var.set(str(info['total_frames']))
    
    def _update_frame_navigation(self):
        """Update the frame navigation controls."""
        if not self.current_frames:
            return
        
        # Update scale
        self.frame_scale.config(to=len(self.current_frames) - 1)
        
        # Update label
        self.frame_label.config(text=f"Frame 0/{len(self.current_frames)}")
        
        # Show first frame
        self._update_gif_preview()
    
    def _update_gif_preview(self, *args):
        """Update the GIF preview."""
        if not self.current_frames:
            return
        
        frame_index = self.frame_var.get()
        if 0 <= frame_index < len(self.current_frames):
            frame = self.current_frames[frame_index]
            
            # Resize for preview
            preview_size = (400, 400)
            frame_resized = self._resize_for_preview(frame, preview_size)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(frame_resized)
            
            # Update canvas
            self.gif_canvas.delete("all")
            x = (self.gif_canvas.winfo_width() - preview_size[0]) // 2
            y = (self.gif_canvas.winfo_height() - preview_size[1]) // 2
            self.gif_canvas.create_image(x, y, anchor="nw", image=photo)
            
            # Keep reference to prevent garbage collection
            self.preview_images = [photo]
            
            # Update label
            self.frame_label.config(text=f"Frame {frame_index + 1}/{len(self.current_frames)}")
    
    def _resize_for_preview(self, image: Image.Image, size: tuple) -> Image.Image:
        """Resize image for preview while maintaining aspect ratio."""
        # Ensure image is in RGBA mode for proper transparency handling
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        image_ratio = image.size[0] / image.size[1]
        preview_ratio = size[0] / size[1]
        
        if image_ratio > preview_ratio:
            new_width = size[0]
            new_height = int(size[0] / image_ratio)
        else:
            new_height = size[1]
            new_width = int(size[1] * image_ratio)
        
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with transparent background
        preview = Image.new('RGBA', size, (255, 255, 255, 0))
        
        # Center the resized image
        x_offset = (size[0] - new_width) // 2
        y_offset = (size[1] - new_height) // 2
        
        # Handle transparency properly - use alpha channel as mask
        if resized.mode == 'RGBA':
            # Extract alpha channel for mask
            alpha = resized.split()[-1]  # Get alpha channel
            # Paste with alpha mask
            preview.paste(resized, (x_offset, y_offset), alpha)
        else:
            # No transparency, paste directly
            preview.paste(resized, (x_offset, y_offset))
        
        return preview
    
    def _generate_sprite_sheet(self):
        """Generate the sprite sheet."""
        if not self.current_frames:
            return
        
        try:
            self.status_bar.config(text="Generating sprite sheet...")
            self.root.update()
            
            # Get settings
            frame_count_str = self.frame_count_var.get()
            frame_count = int(frame_count_str) if frame_count_str != "All" else len(self.current_frames)
            fps = int(self.fps_var.get())
            strategy = self.strategy_var.get()
            optimize_colors = self.optimize_colors_var.get()
            max_colors = int(self.max_colors_var.get())
            
            # Validate settings
            if not (1 <= frame_count <= 64):
                messagebox.showerror("Error", "Frame count must be between 1 and 64")
                return
            
            if not (1 <= fps <= 60):
                messagebox.showerror("Error", "FPS must be between 1 and 60")
                return
            
            # Reduce frames if needed
            if frame_count < len(self.current_frames):
                reduced_frames = self.frame_reducer.reduce_frames(
                    self.current_frames, frame_count, strategy
                )
            else:
                reduced_frames = self.current_frames.copy()
            
            # Generate sprite sheet
            self.status_bar.config(text="Creating sprite sheet...")
            self.root.update()
            self.current_sprite_sheet = self.sprite_generator.create_sprite_sheet(
                reduced_frames, frame_count
            )
            
            # Optimize colors if requested
            if optimize_colors:
                self.status_bar.config(text="Optimizing colors...")
                self.root.update()
                try:
                    # Add a timeout for color optimization
                    import threading
                    import time
                    
                    result = [None]
                    error = [None]
                    
                    def optimize_with_timeout():
                        try:
                            result[0] = self.color_optimizer.optimize_sprite_sheet(
                                self.current_sprite_sheet, max_colors
                            )
                        except Exception as e:
                            error[0] = e
                    
                    # Start optimization in a separate thread
                    thread = threading.Thread(target=optimize_with_timeout)
                    thread.daemon = True
                    thread.start()
                    
                    # Wait for completion with timeout (30 seconds)
                    timeout = 30
                    start_time = time.time()
                    while thread.is_alive() and (time.time() - start_time) < timeout:
                        time.sleep(0.1)
                        self.root.update()
                    
                    if thread.is_alive():
                        # Timeout occurred
                        messagebox.showwarning("Warning", "Color optimization timed out after 30 seconds.\n\nSprite sheet will be saved without color optimization.")
                    elif error[0]:
                        # Error occurred
                        print(f"Color optimization failed: {error[0]}")
                        messagebox.showwarning("Warning", f"Color optimization failed: {str(error[0])}\n\nSprite sheet will be saved without color optimization.")
                    else:
                        # Success
                        self.current_sprite_sheet = result[0]
                        
                except Exception as color_error:
                    print(f"Color optimization failed: {color_error}")
                    messagebox.showwarning("Warning", f"Color optimization failed: {str(color_error)}\n\nSprite sheet will be saved without color optimization.")
            
            # Update sprite sheet preview
            self._update_sprite_preview()
            
            # Enable save button
            self.save_btn.config(state="normal")
            
            self.status_bar.config(text="Sprite sheet generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sprite sheet: {str(e)}")
            self.status_bar.config(text="Error generating sprite sheet")
    
    def _update_sprite_preview(self):
        """Update the sprite sheet preview."""
        if not self.current_sprite_sheet:
            return
        
        # Resize for preview using a simpler method for sprite sheets
        preview_size = (600, 600)
        sprite_resized = self._resize_sprite_for_preview(self.current_sprite_sheet, preview_size)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(sprite_resized)
        
        # Update canvas
        self.sprite_canvas.delete("all")
        x = (self.sprite_canvas.winfo_width() - preview_size[0]) // 2
        y = (self.sprite_canvas.winfo_height() - preview_size[1]) // 2
        self.sprite_canvas.create_image(x, y, anchor="nw", image=photo)
        
        # Keep reference
        self.preview_images.append(photo)
        
        # Update info
        self._update_sprite_info()
    
    def _resize_sprite_for_preview(self, image: Image.Image, size: tuple) -> Image.Image:
        """Resize sprite sheet for preview - simpler method without transparency issues."""
        # Convert to RGB to avoid transparency issues
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_ratio = image.size[0] / image.size[1]
        preview_ratio = size[0] / size[1]
        
        if image_ratio > preview_ratio:
            new_width = size[0]
            new_height = int(size[0] / image_ratio)
        else:
            new_height = size[1]
            new_width = int(size[1] * image_ratio)
        
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create new image with white background
        preview = Image.new('RGB', size, (255, 255, 255))
        
        # Center the resized image
        x_offset = (size[0] - new_width) // 2
        y_offset = (size[1] - new_height) // 2
        preview.paste(resized, (x_offset, y_offset))
        
        return preview
    
    def _update_sprite_info(self):
        """Update the sprite sheet information."""
        if not self.current_sprite_sheet:
            return
        
        # Get sprite sheet info
        frame_count = int(self.frame_count_var.get()) if self.frame_count_var.get() != "All" else len(self.current_frames)
        info = self.sprite_generator.get_sprite_sheet_info(frame_count)
        
        # Get color optimization stats if applicable
        color_stats = ""
        if self.optimize_colors_var.get():
            original = self.sprite_generator.create_sprite_sheet(self.current_frames, frame_count)
            stats = self.color_optimizer.get_optimization_stats(original, self.current_sprite_sheet)
            color_stats = f"""
Color Optimization:
• Original colors: {stats['original_colors']}
• Optimized colors: {stats['optimized_colors']}
• Size reduction: {stats['size_reduction_percent']:.1f}%
"""
        
        info_text = f"""Sprite Sheet Information:
• Size: {info['sprite_sheet_size'][0]}x{info['sprite_sheet_size'][1]} pixels
• Layout: {info['layout_name']} grid
• Frame size: {info['frame_size']}x{info['frame_size']} pixels
• Total cells: {info['total_cells']}
• Used cells: {info['frame_count']}
• Unused cells: {info['unused_cells']}
• FPS: {self.fps_var.get()}{color_stats}"""
        
        self.sprite_info_text.delete(1.0, tk.END)
        self.sprite_info_text.insert(1.0, info_text)
    
    def _save_sprite_sheet(self):
        """Save the sprite sheet."""
        if not self.current_sprite_sheet:
            messagebox.showwarning("Warning", "No sprite sheet to save. Please generate one first.")
            return
        
        try:
            # Generate suggested filename
            if self.current_gif_path:
                base_name = self.filename_parser.extract_base_name(os.path.basename(self.current_gif_path))
                frame_count = int(self.frame_count_var.get()) if self.frame_count_var.get() != "All" else len(self.current_frames)
                fps = int(self.fps_var.get())
                suggested_name = self.filename_parser.generate_filename(base_name, frame_count, fps)
            else:
                suggested_name = "sprite_sheet.png"
            
            # Ask for save location
            file_path = filedialog.asksaveasfilename(
                title="Save Sprite Sheet",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                initialfile=suggested_name
            )
            
            if file_path:
                self.status_bar.config(text="Saving sprite sheet...")
                self.root.update()
                
                # Ensure the sprite sheet is in the right format for saving
                if self.current_sprite_sheet.mode != 'RGBA':
                    self.current_sprite_sheet = self.current_sprite_sheet.convert('RGBA')
                
                self.current_sprite_sheet.save(file_path, "PNG", optimize=True)
                
                self.status_bar.config(text=f"Sprite sheet saved to {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Sprite sheet saved successfully!\n\nFile: {file_path}")
            else:
                self.status_bar.config(text="Save cancelled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sprite sheet: {str(e)}")
            self.status_bar.config(text="Error saving sprite sheet")
