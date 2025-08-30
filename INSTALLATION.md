# Quick Installation Guide

## 🚀 Get Started in 3 Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
# GUI Version (recommended)
python main.py

# Command Line Version
python quick_start.py your_animation.gif
```

### 3. That's it! 🎉

## 📋 What You Get

### GUI Application (`python main.py`)

- **Drag & Drop** GIF files
- **Real-time preview** of original and sprite sheet
- **Interactive controls** for frame count, FPS, and optimization
- **Visual feedback** and progress indicators

### Command Line Tool (`python quick_start.py`)

- **Fast batch processing**
- **Automated filename generation** with VRChat format
- **All the same features** as the GUI

## 🎯 Example Usage

### GUI

1. Run `python main.py`
2. Drag your GIF file into the window
3. Adjust settings (frames, FPS, etc.)
4. Click "Generate Sprite Sheet"
5. Save the result

### Command Line

```bash
# Basic conversion
python quick_start.py animation.gif

# Custom settings
python quick_start.py animation.gif -f 16 -r 20 -o my_sprite.png

# No color optimization (faster)
python quick_start.py animation.gif --no-optimize
```

## 🔧 Advanced Setup (Optional)

### Virtual Environment (Recommended)

```bash
python -m venv pixie-env
pixie-env\Scripts\activate  # Windows
source pixie-env/bin/activate  # macOS/Linux
pip install -r requirements.txt
python main.py
```

## ✅ System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, macOS, or Linux
- **Memory**: 2GB+ RAM (for large GIFs)
- **Storage**: Minimal (just the application files)

## 🆘 Need Help?

- **Check the README.md** for detailed documentation
- **Run the test script**: `python test_app.py`
- **Try the command line tool** first: `python quick_start.py --help`

## 🎨 VRChat Integration

The generated sprite sheets are ready to upload to VRChat:

- **Size**: 1024x1024 pixels
- **Format**: PNG with transparency
- **Grid**: Automatic 2x2, 4x4, or 8x8 layout
- **Filename**: Supports VRChat's format (e.g., "Name_14frames_20fps.png")

---

**Ready to create amazing VRChat animations? Start with `python main.py`!** 🎮✨
