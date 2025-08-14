# svg.py
from pathlib import Path
import shutil
import subprocess
import os

# We'll prefer wand (ImageMagick) if available, else try cairosvg

def convert_svg(src: Path, dst: Path) -> bool:
    # try wand (ImageMagick) via "magick" or "convert"
    try:
        # ImageMagick: magick input.svg output.png
        magick_cmd = shutil.which("magick") or shutil.which("convert")
        if magick_cmd:
            cmd = [magick_cmd, str(src), str(dst)]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
            return dst.exists()
    except Exception:
        pass

    # try cairosvg python lib
    try:
        import cairosvg
        # choose png/pdf by dst suffix
        suf = dst.suffix.lower()
        if suf in (".png", ".jpg", ".jpeg"):
            cairosvg.svg2png(url=str(src), write_to=str(dst))
        elif suf == ".pdf":
            cairosvg.svg2pdf(url=str(src), write_to=str(dst))
        else:
            cairosvg.svg2png(url=str(src), write_to=str(dst))
        return dst.exists()
    except Exception:
        pass

    return False
