# image.py
from pathlib import Path
from PIL import Image

def convert_image(src: Path, dst: Path, target: str) -> bool:
    try:
        with Image.open(src) as img:
            if target in ("jpg","jpeg"):
                if img.mode in ("RGBA","LA"):
                    bg = Image.new("RGB", img.size, (255,255,255))
                    bg.paste(img, mask=img.split()[-1])
                    img = bg
                img = img.convert("RGB")
                img.save(dst, "JPEG", quality=85, optimize=True)
            else:
                img.save(dst, target.upper())
        return True
    except Exception:
        return False
