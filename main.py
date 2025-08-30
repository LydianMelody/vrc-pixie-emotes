#!/usr/bin/env python3
"""
PIXIE — Pixel Image eXporter for Instant Emotes

Main application entry point for converting GIF files to VRChat-compatible sprite sheets.
"""

import tkinter as tk
import sys
import os
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Create root window
    root = tk.Tk()
    
    # Set application icon
    try:
        icon_path = Path(__file__).parent / "ui" / "PixieLogo.png"
        if icon_path.exists():
            # Convert PNG to ICO format for Windows
            from PIL import Image
            img = Image.open(icon_path)
            # Create a temporary ICO file
            ico_path = Path(__file__).parent / "temp_icon.ico"
            img.save(ico_path, format='ICO', sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128)])
            root.iconbitmap(str(ico_path))
            # Clean up temporary file
            ico_path.unlink(missing_ok=True)
    except Exception as e:
        print(f"Could not set application icon: {e}")
    
    # Create main window
    app = MainWindow(root)
    
    # Start the application
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
