#!/usr/bin/env python3
"""
Eel application bridge exposing existing GIF processing logic to a web UI.
"""

import sys
import json
from pathlib import Path
import threading
import base64
import uuid

import eel
import shutil
import atexit

# Ensure project root (and thus `src`) is importable
sys.path.insert(0, str(Path(__file__).parent))

from src.gif_processor import GIFProcessor
from src.sprite_generator import VRChatSpriteGenerator
from src.color_optimizer import ColorOptimizer
from src.utils.filename_parser import FilenameParser
from src.utils.frame_reducer import FrameReducer


PROJECT_ROOT = Path(__file__).parent
WEB_DIR = PROJECT_ROOT / "web"
TMP_DIR = WEB_DIR / "tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)


def _safe_rmtree(path: Path):
    try:
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass


def _cleanup_tmp():
    # Remove transient previews and frames; keep folder
    try:
        # Remove frames subfolders and known previews
        frames_dir = TMP_DIR / "frames"
        _safe_rmtree(frames_dir)
        for name in ("original_preview.gif", "preview.png", "sheet_preview.jpg"):
            try:
                p = TMP_DIR / name
                if p.exists():
                    p.unlink()
            except Exception:
                pass
        # Recreate frames dir for next run
        (TMP_DIR / "frames").mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


# Clean temp on process exit
atexit.register(_cleanup_tmp)


class AppState:
    def __init__(self):
        self.gif_processor = None
        self.current_gif_path = None
        self.current_frames = []
        self.sprite_generator = VRChatSpriteGenerator()
        self.color_optimizer = ColorOptimizer()
        self.filename_parser = FilenameParser()
        self.frame_reducer = FrameReducer()
        self.current_sprite_sheet = None
        self.last_frame_count = None
        self.last_fps = None


STATE = AppState()


@eel.expose
def open_file_dialog() -> str:
    """Open a native file dialog through Tk to select a GIF file."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title="Select GIF File", filetypes=[("GIF files", "*.gif"), ("All files", "*.*")])
        root.destroy()
        return path
    except Exception:
        return ""


@eel.expose
def load_gif(path: str):
    """Load a GIF and return basic info plus a preview thumbnail path under web/tmp."""
    try:
        eel.py_log(f"Loading GIF: {Path(path).name}")
    except Exception:
        pass
    STATE.gif_processor = GIFProcessor(path)
    STATE.current_gif_path = path
    STATE.current_frames = STATE.gif_processor.get_frames()

    info = STATE.gif_processor.get_frame_info()

    # Save a still PNG (first frame) and an animated GIF preview
    from PIL import Image
    frames = STATE.current_frames
    if not frames:
        return {"message": "No frames found"}

    def _resize(img: Image.Image, max_side: int = 520) -> Image.Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        w, h = img.size
        scale = min(1.0, max_side / max(w, h))
        if scale < 1.0:
            img = img.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.Resampling.LANCZOS)
        return img

    resized_frames = [_resize(f) for f in frames]
    first_png = resized_frames[0]

    still_path = TMP_DIR / "preview.png"
    first_png.save(still_path, "PNG", optimize=True)

    # Animated preview GIF
    durations = info.get("frame_durations") or [100] * len(resized_frames)
    try:
        anim_path = TMP_DIR / "original_preview.gif"
        first_png.save(
            anim_path,
            format="GIF",
            save_all=True,
            append_images=resized_frames[1:],
            duration=[max(20, int(d)) for d in durations[: len(resized_frames)]],
            loop=0,
            disposal=2,
            optimize=True,
        )
        original_preview = f"/tmp/{anim_path.name}"
    except Exception:
        original_preview = f"/tmp/{still_path.name}"

    # Also export frame-by-frame PNGs for precise canvas playback (cap at 64)
    export_count = min(len(resized_frames), 64)
    session_id = uuid.uuid4().hex[:8]
    session_dir = TMP_DIR / "frames" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    frame_meta = []
    for idx in range(export_count):
        p = session_dir / f"frame_{idx:03d}.png"
        resized_frames[idx].save(p, "PNG", optimize=True)
        frame_meta.append({
            "path": f"/tmp/frames/{session_id}/frame_{idx:03d}.png",
            "duration": max(20, int(durations[idx] if idx < len(durations) else 100)),
        })

    return {
        "total_frames": info["total_frames"],
        "original_dimensions": info["original_dimensions"],
        "loop_count": info["loop_count"],
        "average_duration": info.get("average_duration", 0),
        "frame_durations": info.get("frame_durations", []),
        "preview_path": f"/tmp/{still_path.name}",
        "original_preview_path": original_preview,
        "frames": frame_meta,
    }


@eel.expose
def import_gif_bytes(b64: str, filename: str):
    """Accept a GIF from the browser via base64, write to tmp, and load it."""
    safe_name = Path(filename).name
    # Force .gif extension to avoid serving unexpected content types
    if not safe_name.lower().endswith('.gif'):
        safe_name = f"{Path(safe_name).stem}.gif"
    target = TMP_DIR / safe_name
    try:
        data = base64.b64decode(b64, validate=True)
    except Exception:
        return {"message": "Invalid upload data"}
    # Basic signature check for GIF (GIF87a or GIF89a)
    if not (len(data) >= 6 and (data[:6] in (b"GIF87a", b"GIF89a"))):
        return {"message": "Not a GIF file"}
    try:
        target.write_bytes(data)
    except Exception as e:
        return {"message": f"Failed to write temp file: {e}"}
    return load_gif(str(target))


@eel.expose
def generate_sprite_sheet(settings_json: str | dict):
    """Generate the sprite sheet using provided settings.
    settings: { optimize: bool, maxColors: int, strategy: str, fps: int, frameCount?: int }
    """
    if isinstance(settings_json, str):
        try:
            settings = json.loads(settings_json)
        except Exception:
            settings = {}
    else:
        settings = dict(settings_json)

    if not STATE.current_frames:
        return {"message": "No GIF loaded"}

    frame_count = settings.get("frameCount") or len(STATE.current_frames)
    fps = int(settings.get("fps", 10))
    # Strategy removed from UI; emulate with remove-every pattern
    strategy = 'every_nth'
    optimize = bool(settings.get("optimize", True))
    max_colors = int(settings.get("maxColors", 256))

    # Interpret removeEvery: 0=no removal, 1=keep1 drop1, 2=keep2 drop1, ...
    remove_every = int(settings.get('removeEvery', settings.get('nth', 0)) or 0)
    nth = (remove_every + 1) if remove_every > 0 else None
    # Always call reducer to respect explicit nth skipping even when target_count equals original length
    # Apply remove-every first, then enforce target_count using reducer
    frames_initial = STATE.current_frames
    if remove_every > 0:
        frames_initial = STATE.frame_reducer.remove_every(frames_initial, keep_r=remove_every)
    frames = STATE.frame_reducer.reduce_frames(frames_initial, frame_count, strategy, nth=nth)
    try:
        eel.py_log("Creating sprite sheet…")
    except Exception:
        pass
    # Use the actual count of frames after reduction for sheet layout and filename suggestions
    actual_frame_count = len(frames)
    STATE.current_sprite_sheet = STATE.sprite_generator.create_sprite_sheet(frames, actual_frame_count)
    # Persist settings for filename suggestion
    STATE.last_frame_count = actual_frame_count
    STATE.last_fps = fps

    if optimize:
        try:
            eel.py_log("Optimizing colors…")
            STATE.current_sprite_sheet = STATE.color_optimizer.optimize_sprite_sheet(STATE.current_sprite_sheet, max_colors)
        except Exception:
            pass

    # Save preview
    from PIL import Image
    sheet = STATE.current_sprite_sheet
    if sheet.mode != 'RGB':
        sheet = sheet.convert('RGB')
    preview_path = TMP_DIR / "sheet_preview.jpg"
    sheet.save(preview_path, "JPEG", quality=85, optimize=True)

    try:
        eel.py_log("Sprite sheet generated.")
    except Exception:
        pass
    return {"message": "Sprite sheet generated", "preview_path": f"/tmp/{preview_path.name}"}


@eel.expose
def save_sprite_sheet():
    """Save the generated sprite sheet as PNG using a native dialog."""
    if STATE.current_sprite_sheet is None:
        return {"ok": False, "message": "No sprite sheet to save."}
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox

        root = tk.Tk()
        root.withdraw()
        suggested = "sprite_sheet.png"
        if STATE.current_gif_path:
            base = STATE.filename_parser.extract_base_name(Path(STATE.current_gif_path).name)
            frame_count = STATE.last_frame_count or len(STATE.current_frames)
            fps = int(STATE.last_fps or 10)
            suggested = STATE.filename_parser.generate_filename(base, frame_count, fps)
        path = filedialog.asksaveasfilename(
            title="Save Sprite Sheet",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=suggested,
        )
        root.destroy()
        if not path:
            return {"ok": False, "message": "Save cancelled."}
        sheet = STATE.current_sprite_sheet
        if sheet.mode != 'RGBA':
            sheet = sheet.convert('RGBA')
        sheet.save(path, "PNG", optimize=True)
        return {"ok": True, "message": f"Saved to {Path(path).name}"}
    except Exception as e:
        return {"ok": False, "message": f"Error: {e}"}


def main():
    # Prepare web assets (copy logo into web assets for serving)
    assets_dir = WEB_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    logo_src = PROJECT_ROOT / "ui" / "PixieLogo.png"
    if logo_src.exists():
        try:
            shutil.copyfile(logo_src, assets_dir / "PixieLogo.png")
        except Exception:
            pass

    # Clean tmp at startup
    _cleanup_tmp()

    eel.init(str(WEB_DIR))
    # Let Eel choose the available/default browser (no forced mode)
    eel.start("index.html", size=(1200, 900))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ensure cleanup then exit
        try:
            _cleanup_tmp()
        except Exception:
            pass
        raise


