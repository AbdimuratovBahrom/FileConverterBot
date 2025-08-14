# audio.py
from pathlib import Path
import shutil
import subprocess

def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def convert_audio(src: Path, dst: Path, target: str) -> bool:
    if not has_ffmpeg():
        return False
    cmd = ["ffmpeg", "-y", "-i", str(src), "-vn", "-acodec", "libmp3lame" if target=="mp3" else "aac" , str(dst)]
    # simplified codec selection; ffmpeg will usually pick appropriate defaults
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        return dst.exists()
    except Exception:
        # fallback simple ffmpeg call
        try:
            subprocess.run(["ffmpeg","-y","-i",str(src), str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
            return dst.exists()
        except Exception:
            return False
