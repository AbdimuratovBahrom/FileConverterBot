# video.py
from pathlib import Path
import shutil
import subprocess

def has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None

def convert_video(src: Path, dst: Path, target: str) -> bool:
    if not has_ffmpeg():
        return False
    try:
        cmd = ["ffmpeg", "-y", "-i", str(src), "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", str(dst)]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1200)
        return dst.exists()
    except Exception:
        # try simpler
        try:
            subprocess.run(["ffmpeg","-y","-i",str(src), str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=1200)
            return dst.exists()
        except Exception:
            return False

def extract_audio_from_video(src: Path, dst: Path, target_audio_ext: str) -> bool:
    if not has_ffmpeg():
        return False
    try:
        cmd = ["ffmpeg", "-y", "-i", str(src), "-vn", "-acodec", "copy", str(dst)]
        # if copy doesn't match target, do re-encode
        res = subprocess.run(cmd)
        if dst.exists():
            return True
    except Exception:
        pass
    # re-encode
    try:
        subprocess.run(["ffmpeg","-y","-i",str(src), "-vn", str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
        return dst.exists()
    except Exception:
        return False
