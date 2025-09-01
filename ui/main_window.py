"""
Main GUI Window for VRChat GIF Maker

Provides a user-friendly interface with drag-and-drop functionality and preview capabilities.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter import font as tkfont
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
        self.is_playing = False
        self.play_after_id = None
        self.frame_durations = []
        
        # Fonts
        self._setup_fonts()

        self._setup_ui()
        self._setup_drag_drop()
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Apply a soft pastel kawaii-inspired theme using ttk styles
        self._apply_kawaii_style()
        # Max preview size to avoid overly large images
        self.max_preview_size = 520
        
        # Grid: header, content, status bar
        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        # Header
        self._create_header()

        # Content area with two columns
        self.content_frame = ttk.Frame(self.root)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(6, 6))
        self.content_frame.grid_columnconfigure(0, weight=2)
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Left: preview area; Right: controls
        self.preview_container = ttk.Frame(self.content_frame)
        self.preview_container.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.controls_container = ttk.Frame(self.content_frame)
        self.controls_container.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # Build inner content
        self._create_main_area(self.preview_container)
        self._create_sidebar(self.controls_container)

        # Status bar removed; we surface status in GIF Information panel

    def _create_header(self):
        """Create compact header with logo and title."""
        header = ttk.Frame(self.root, padding=(10, 6))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        # Logo (small)
        try:
            logo_path = Path(__file__).parent / "PixieLogo.png"
            if logo_path.exists():
                img = Image.open(logo_path)
                size = 44
                img = img.resize((size, int(size * img.height / img.width)), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                logo = ttk.Label(header, image=photo)
                logo.image = photo
                logo.grid(row=0, column=0, sticky="w")
            else:
                ttk.Label(header, text="PIXIE", font=(self.font_family, 16, "bold")).grid(row=0, column=0, sticky="w")
        except Exception:
            ttk.Label(header, text="PIXIE", font=(self.font_family, 16, "bold")).grid(row=0, column=0, sticky="w")
        # Title
        title = ttk.Label(header, text="Pixel Image eXporter for Instant Emotes", font=(self.font_family, 13))
        title.grid(row=0, column=1, sticky="w", padx=(10, 0))

    def _apply_kawaii_style(self):
        """Create a custom ttk style with pastel colors and rounded elements."""
        try:
            style = ttk.Style(self.root)
            # Use a base theme for compatibility
            base = 'clam' if 'clam' in style.theme_names() else style.theme_use()
            style.theme_use(base)
            # Palette
            self.theme_bg = '#fff0fa'      # blush pink
            self.theme_panel = '#ffffff'   # white panels
            self.theme_accent = '#b3d8ff'  # baby blue accents (light)
            self.theme_accent2 = '#ffd9ec' # light pink accent
            self.theme_text = '#333333'
            # Root window bg
            self.root.configure(background=self.theme_bg)
            # Frames & labels
            style.configure('TFrame', background=self.theme_bg)
            style.configure('TLabelframe', background=self.theme_bg, relief='flat')
            style.configure('TLabelframe.Label', background=self.theme_bg, foreground=self.theme_text)
            style.configure('TLabel', background=self.theme_bg, foreground=self.theme_text)
            # Buttons
            style.configure('TButton', background=self.theme_accent, foreground=self.theme_text, padding=6)
            style.map('TButton', background=[('active', self.theme_accent2)])
            # Entry/Combobox
            style.configure('TEntry', fieldbackground=self.theme_panel, background=self.theme_panel)
            style.configure('TCombobox', fieldbackground=self.theme_panel, background=self.theme_panel)
            # Notebook
            style.configure('TNotebook', background=self.theme_bg, tabmargins=[8, 4, 8, 0])
            style.configure('TNotebook.Tab', padding=[12, 6], background=self.theme_accent2)
            style.map('TNotebook.Tab', background=[('selected', self.theme_accent)], expand=[('selected', [1, 1, 1, 0])])
            # Status bar label
            style.configure('Status.TLabel', background=self.theme_accent2, foreground=self.theme_text)
        except Exception:
            # Fail silently if style cannot be applied on this platform
            pass
    
    def _setup_fonts(self):
        """Configure application fonts to use Open Sans if available, with Arial fallback."""
        try:
            available_families = set(f for f in tkfont.families(self.root))
            self.font_family = 'Open Sans' if 'Open Sans' in available_families else 'Arial'
            # Update Tk named fonts so all widgets inherit the family unless overridden
            for name in [
                'TkDefaultFont', 'TkTextFont', 'TkMenuFont', 'TkHeadingFont',
                'TkCaptionFont', 'TkSmallCaptionFont', 'TkIconFont', 'TkTooltipFont'
            ]:
                try:
                    named = tkfont.nametofont(name)
                    named.configure(family=self.font_family)
                except Exception:
                    pass
        except Exception:
            # Fallback if font handling fails
            self.font_family = 'Arial'

    def _create_sidebar(self, parent: ttk.Frame):
        """Create a scrollable controls panel on the right."""
        sidebar = ttk.Frame(parent)
        sidebar.pack(fill="both", expand=True)

        container = ttk.Frame(sidebar)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, highlightthickness=0, bg=self.theme_bg, bd=0)
        vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas, padding="10")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)
        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")
        
        # Minimal header in controls
        ttk.Label(scroll_frame, text="Controls", font=(self.font_family, 12, "bold")).pack(anchor="w", pady=(0, 8))
        
        # File selection
        file_frame = ttk.LabelFrame(scroll_frame, text="File Selection", padding="10")
        file_frame.pack(fill="x", pady=(0, 10))
        
        self.file_label = ttk.Label(file_frame, text="No file selected", wraplength=200)
        self.file_label.pack(pady=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse GIF", command=self._browse_file)
        browse_btn.pack(fill="x")
        
        # GIF Information
        self.info_frame = ttk.LabelFrame(scroll_frame, text="GIF Information", padding="10")
        self.info_frame.pack(fill="x", pady=(0, 10))
        
        # Status line inside GIF Information
        self.status_var = tk.StringVar(value="")
        self.status_label = ttk.Label(self.info_frame, textvariable=self.status_var)
        self.status_label.pack(anchor="w", pady=(0, 6))

        self.info_text = tk.Text(self.info_frame, height=8, width=30, wrap="word")
        self.info_text.pack(fill="both", expand=True)
        
        # Settings
        settings_frame = ttk.LabelFrame(scroll_frame, text="Settings", padding="10")
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
    
    def _create_main_area(self, parent: ttk.Frame):
        """Create the main area with preview."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=(5, 10), pady=10)
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
        # Redraw preview when canvas size changes
        self.gif_canvas.bind("<Configure>", lambda e: self._update_gif_preview())
        # Draw pastel checkerboard background
        self._decorate_checkerboard(self.gif_canvas)
        
        # Frame navigation
        nav_frame = ttk.Frame(gif_frame)
        nav_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.frame_var = tk.IntVar(value=0)
        self.frame_scale = ttk.Scale(nav_frame, from_=0, to=0, variable=self.frame_var, 
                                    orient="horizontal", command=self._on_frame_slider)
        self.frame_scale.pack(fill="x", side="left", expand=True)
        
        # Playback controls
        controls = ttk.Frame(nav_frame)
        controls.pack(side="right", padx=(10, 0))
        ttk.Button(controls, text="Play", command=self._play_gif).pack(side="left", padx=(0, 4))
        ttk.Button(controls, text="Pause", command=self._pause_gif).pack(side="left", padx=(0, 4))
        ttk.Button(controls, text="Stop", command=self._stop_gif).pack(side="left")
        
        self.frame_label = ttk.Label(nav_frame, text="Frame 0/0")
        self.frame_label.pack(side="right", padx=(10, 0))
    
    def _create_sprite_tab(self):
        """Create the sprite sheet preview tab."""
        sprite_frame = ttk.Frame(self.notebook)
        self.notebook.add(sprite_frame, text="Sprite Sheet")
        
        # Sprite sheet preview
        self.sprite_canvas = tk.Canvas(sprite_frame, bg="white")
        self.sprite_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        # Redraw preview when canvas size changes
        self.sprite_canvas.bind("<Configure>", lambda e: self._update_sprite_preview())
        # Draw pastel checkerboard background
        self._decorate_checkerboard(self.sprite_canvas)
        
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
        """Deprecated: status is shown in GIF Information box."""
        pass
    
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
            self._set_status("Loading GIF...")
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
            
            self._set_status("GIF loaded successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load GIF: {str(e)}")
            self._set_status("Error loading GIF")
    
    def _update_gif_info(self):
        """Update the GIF information display."""
        if not self.gif_processor:
            return
        
        info = self.gif_processor.get_frame_info()
        # Save durations for playback
        self.frame_durations = info.get('frame_durations', [])
        
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
            
            # Resize for preview based on current canvas size with a max cap
            preview_size = (
                min(self.max_preview_size, max(100, self.gif_canvas.winfo_width() - 20)),
                min(self.max_preview_size, max(100, self.gif_canvas.winfo_height() - 20))
            )
            frame_resized = self._resize_for_preview(frame, preview_size)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(frame_resized)
            
            # Update canvas
            self.gif_canvas.delete("all")
            self._decorate_checkerboard(self.gif_canvas)
            canvas_w = self.gif_canvas.winfo_width()
            canvas_h = self.gif_canvas.winfo_height()
            x = (canvas_w - frame_resized.width) // 2
            y = (canvas_h - frame_resized.height) // 2
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
        orig_w, orig_h = image.size
        max_w, max_h = size
        scale = min(1.0, max_w / orig_w, max_h / orig_h)
        if scale < 1.0:
            new_size = (max(1, int(orig_w * scale)), max(1, int(orig_h * scale)))
            return image.resize(new_size, Image.Resampling.LANCZOS)
        # Do not upscale small images
        return image

    def _on_frame_slider(self, *args):
        """Pause playback when user scrubs and update preview."""
        self._pause_gif()
        self._update_gif_preview()

    def _play_gif(self):
        if not self.current_frames:
            return
        if self.is_playing:
            return
        self.is_playing = True
        self._schedule_next_frame()

    def _pause_gif(self):
        self.is_playing = False
        if self.play_after_id is not None:
            try:
                self.root.after_cancel(self.play_after_id)
            except Exception:
                pass
            self.play_after_id = None

    def _stop_gif(self):
        self._pause_gif()
        if self.current_frames:
            self.frame_var.set(0)
            self._update_gif_preview()

    def _schedule_next_frame(self):
        if not self.is_playing or not self.current_frames:
            return
        # Advance frame
        next_index = (self.frame_var.get() + 1) % len(self.current_frames)
        self.frame_var.set(next_index)
        self._update_gif_preview()
        # Determine delay
        delay = 100
        try:
            if self.frame_durations and 0 <= next_index < len(self.frame_durations):
                delay = max(20, int(self.frame_durations[next_index]))
        except Exception:
            pass
        self.play_after_id = self.root.after(delay, self._schedule_next_frame)
    
    def _generate_sprite_sheet(self):
        """Generate the sprite sheet."""
        if not self.current_frames:
            return
        
        try:
            self._set_status("Generating sprite sheet...")
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
            self._set_status("Creating sprite sheet...")
            self.root.update()
            self.current_sprite_sheet = self.sprite_generator.create_sprite_sheet(
                reduced_frames, frame_count
            )
            
            # Optimize colors if requested
            if optimize_colors:
                self._set_status("Optimizing colors...")
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
            
            self._set_status("Sprite sheet generated successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate sprite sheet: {str(e)}")
            self._set_status("Error generating sprite sheet")
    
    def _update_sprite_preview(self):
        """Update the sprite sheet preview."""
        if not self.current_sprite_sheet:
            return
        
        # Refresh background
        self._decorate_checkerboard(self.sprite_canvas)

        # Resize for preview based on current canvas size with a max cap
        canvas_w = self.sprite_canvas.winfo_width()
        canvas_h = self.sprite_canvas.winfo_height()
        preview_size = (
            min(self.max_preview_size, max(100, canvas_w - 20)),
            min(self.max_preview_size, max(100, canvas_h - 20))
        )
        sprite_resized = self._resize_sprite_for_preview(self.current_sprite_sheet, preview_size)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(sprite_resized)
        
        # Update canvas
        self.sprite_canvas.delete("all")
        x = (canvas_w - sprite_resized.width) // 2
        y = (canvas_h - sprite_resized.height) // 2
        self.sprite_canvas.create_image(x, y, anchor="nw", image=photo)
        
        # Keep reference
        self.preview_images.append(photo)
        
        # Update info
        self._update_sprite_info()

    def _decorate_checkerboard(self, canvas: tk.Canvas):
        """Draw a soft pastel checkerboard background on a canvas."""
        try:
            canvas.delete("bg")
        except Exception:
            pass
        width = max(0, canvas.winfo_width())
        height = max(0, canvas.winfo_height())
        if width == 0 or height == 0:
            return
        tile = 24
        color_a = "#fff6fb"  # very light pink
        color_b = "#f2f8ff"  # very light blue
        for y in range(0, height, tile):
            for x in range(0, width, tile):
                fill = color_a if ((x // tile + y // tile) % 2 == 0) else color_b
                canvas.create_rectangle(x, y, x + tile, y + tile, fill=fill, outline=fill, tags="bg")
    
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
                self._set_status("Saving sprite sheet...")
                self.root.update()
                
                # Ensure the sprite sheet is in the right format for saving
                if self.current_sprite_sheet.mode != 'RGBA':
                    self.current_sprite_sheet = self.current_sprite_sheet.convert('RGBA')
                
                self.current_sprite_sheet.save(file_path, "PNG", optimize=True)
                
                self._set_status(f"Sprite sheet saved to {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"Sprite sheet saved successfully!\n\nFile: {file_path}")
            else:
                self._set_status("Save cancelled")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save sprite sheet: {str(e)}")
            self._set_status("Error saving sprite sheet")

    def _set_status(self, text: str):
        """Update status text in the GIF Information panel."""
        try:
            if hasattr(self, 'status_var') and self.status_var is not None:
                self.status_var.set(text)
        except Exception:
            pass
