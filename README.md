# PIXIE — Pixel Image eXport for Instant Emotes

A beautiful Python application by **LydianMelody** that converts GIF files to VRChat‑compatible sprite sheets with smart frame handling and color optimization.

![PIXIE Logo](ui/PixieLogo.png)

## ✨ What PIXIE does now

### 🎯 Core

- **GIF processing**: Loads frames and preserves per‑frame durations
- **Sprite sheet generation**: Outputs VRChat‑ready 1024×1024 sheets
- **Frame management**: "Remove every Nth" control (keep R, drop 1) plus uniform reduction when needed
- **Color optimization**: Palette reduction to shrink file size while keeping quality
- **Smart filenames**: Suggests names like `MyEmoji_14frames_20fps.png` using the **actual reduced frame count** and FPS

### 🎨 VRChat compatibility

- **Grid layouts** (auto‑selected):
  - 2×2 (512×512 per frame) for up to 4 frames
  - 4×4 (256×256 per frame) for up to 16 frames
  - 8×8 (128×128 per frame) for up to 64 frames
- **Ordering**: Frames placed left‑to‑right, then top‑to‑bottom
- **Irregular counts**: Extra cells in the grid remain unused (hidden in VRChat)

### 🖥️ Web UI (Eel)

- **Tabs**: Original, Sprite, and Help & Info
- **Drag & drop**: Drop a `.gif` onto the preview or click Browse
- **Canvas player**: Accurate frame‑by‑frame preview with play/pause/stop
- **Controls**: Remove‑every, FPS, Optimize colors, Max colors
- **Help & Info**: Built‑in summary of VRChat sprite sheet rules and About
- **Cute brutalist buttons**: Square edges, sheen hover, punchy shadows, reduced‑motion friendly

### 🚀 Performance & Optimization

- **Fast**: Vectorized image operations and efficient sampling
- **Memory‑friendly**: Works well with typical emote‑sized GIFs
- **Graceful fallbacks**: Keeps going if an optimization step fails

## 🛠️ Installation

### Prerequisites

- Python 3.8+ (tested on Windows; macOS/Linux should work but are not fully tested)
- A Chromium‑based browser (Chrome, Edge, Brave, etc). The app opens in your default browser; if no Chromium‑based browser is available, install one or configure `eel_app.py` with a specific `mode`.

### Quick Setup

1. **Clone or download** this repository
2. **Navigate** to the project directory
3. **Create virtual environment** (recommended):

   ```bash
   python -m venv pixie-env
   pixie-env\Scripts\activate  # Windows
   source pixie-env/bin/activate  # macOS/Linux
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

### Web UI (Recommended)

```bash
# From the project root
python eel_app.py
```

By default, PIXIE opens in your system default browser. For most users this will be a Chromium‑based browser. If you need to force a browser, you can set the `mode` argument in `eel_app.py` (e.g., `mode="chrome"`, `mode="edge"`, or `mode="electron"`).

**How to use:**

- Browse or drag a `.gif` into the preview
- Optionally set Remove‑every, FPS, and color limits
- Click Generate Sprite → preview appears under the Sprite tab
- Click Save PNG → a suggested filename is provided based on the loaded GIF and the actual reduced frame count and FPS

### Classic desktop UI (Tkinter)

```bash
python main.py
```

### Command line quick start

```bash
python quick_start.py animation.gif -o output.png -f 16 -r 20
```

## 📁 Project Structure

```text
PIXIE/
├── eel_app.py              # Web UI entry (Eel)
├── web/                    # Web assets
│   ├── index.html          # UI layout (tabs, preview, controls)
│   ├── styles.css          # Styling (brutalist buttons, layout)
│   └── app.js              # Client logic & Eel calls
├── main.py                 # Classic desktop UI (Tkinter)
├── quick_start.py          # Command line interface
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── ui/
│   ├── main_window.py     # Tkinter implementation
│   └── PixieLogo.png      # Application logo
├── src/
│   ├── gif_processor.py   # GIF loading and frame extraction
│   ├── sprite_generator.py # Sprite sheet generation
│   ├── color_optimizer.py # Color palette optimization
│   └── utils/
│       ├── filename_parser.py # VRChat filename handling
│       └── frame_reducer.py   # Frame reduction strategies
└── examples/              # Sample files and documentation
```

## 🎯 Frame reduction

- **every_nth**: UI control for "keep R, drop 1" (e.g., 1→keep one, drop one)
- **uniform / keep_ends**: Used internally when a precise target is required

## 🔧 Technical Details

### Dependencies

- **Pillow (PIL)**: Image processing and manipulation
- **imageio**: GIF loading and frame extraction
- **numpy**: Numerical operations for color optimization
- **tkinter**: Classic desktop UI (included with Python)
- **Eel**: Lightweight Python↔web bridge for the new web UI

### Performance Features

- **Vectorized Operations**: Fast numpy-based color processing
- **Smart Sampling**: Reduces memory usage for large images
- **Timeout Protection**: Prevents infinite processing
- **Error Recovery**: Graceful fallbacks for optimization failures

## 🎵 About PIXIE

**PIXIE** (Pixel Image eXport for Instant Emotes) was created by **LydianMelody** to help VRChat players easily convert GIF animations into compatible sprite sheets. The app now includes a modern web UI with playful brutalist styling and built‑in guidance for VRChat’s sprite sheet rules.

## 📋 TODO

### 🎨 UI/UX Improvements

- [ ] **Responsive Design**: Make the interface adapt to different window sizes
- [ ] **Beautiful UI**: Enhance visual design with modern styling and animations
- [ ] **Dark Mode**: Add optional dark theme for better accessibility
- [ ] **Custom Themes**: Allow users to customize the interface appearance
- [ ] **Better Typography**: Improve font choices and text hierarchy
- [ ] **Smooth Animations**: Add subtle animations for better user experience
- [ ] **Accessibility**: Improve keyboard navigation and screen reader support

### 🔧 Technical Enhancements

- [ ] **Batch Processing**: Process multiple GIFs at once
- [ ] **Preset Management**: Save and load custom settings
- [ ] **Export Formats**: Support additional output formats
- [ ] **Advanced Preview**: Zoom and pan capabilities for sprite sheet preview
- [ ] **Undo/Redo**: Add history management for settings changes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

Licensed under the Apache License, Version 2.0. See `LICENSE` for details.
Attribution is appreciated; see `NOTICE` for guidance.

## 🎵 Support

If PIXIE helped you, awesome — have a lovely day!

---

<!-- markdownlint-disable-next-line MD036 -->
*Made with ❤️ and 🎵 by LydianMelody*
