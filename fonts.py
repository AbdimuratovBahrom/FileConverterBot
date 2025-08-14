# fonts.py
from pathlib import Path
import shutil
import subprocess

def convert_font(src: Path, dst: Path, target_ext: str) -> bool:
    # Prefer fontforge CLI
    ff = shutil.which("fontforge")
    if ff:
        try:
            # fontforge -lang=ff -c 'Open($1); Generate($2)' in out
            cmd = [ff, "-lang=ff", "-c", f'Open("{str(src)}"); Generate("{str(dst)}")']
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
            return dst.exists()
        except Exception:
            pass

    # Try fonttools (woff -> ttf etc.) using ttLib for some types (limited)
    try:
        from fontTools.ttLib import TTFont
        sfx = src.suffix.lower().lstrip(".")
        dfx = dst.suffix.lower().lstrip(".")
        # Only certain conversions possible; try load/save for ttf/otf
        if sfx in ("ttf","otf") and dfx in ("ttf","otf"):
            font = TTFont(str(src))
            font.save(str(dst))
            return dst.exists()
    except Exception:
        pass

    return False
