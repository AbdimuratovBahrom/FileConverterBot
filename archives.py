# archives.py
from pathlib import Path
import zipfile
import tarfile
import shutil
import subprocess
import os

def archive_extract_then_pack(src: Path, extract_to: Path, target_format: str, out_path: Path) -> bool:
    # extract
    try:
        extract_to.mkdir(parents=True, exist_ok=True)
        suf = src.suffix.lower().lstrip(".")
        if suf == "zip":
            with zipfile.ZipFile(src, "r") as z:
                z.extractall(extract_to)
        elif suf in ("tar","gz","tgz"):
            with tarfile.open(src, "r:*") as t:
                t.extractall(extract_to)
        elif suf == "7z":
            seven = shutil.which("7z")
            if not seven:
                return False
            subprocess.run([seven, "x", str(src), f"-o{str(extract_to)}", "-y"], check=True)
        elif suf == "rar":
            # try unrar or 7z
            unrar = shutil.which("unrar")
            if unrar:
                subprocess.run([unrar, "x", "-y", str(src), str(extract_to)], check=True)
            else:
                seven = shutil.which("7z")
                if seven:
                    subprocess.run([seven, "x", str(src), f"-o{str(extract_to)}", "-y"], check=True)
                else:
                    return False
        else:
            return False
    except Exception:
        return False

    # pack into target_format
    return archive_create_from_dir(extract_to, out_path)

def archive_create_from_dir(src_dir: Path, out_path: Path) -> bool:
    try:
        ext = out_path.suffix.lower().lstrip(".")
        if ext == "zip":
            with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(src_dir):
                    for f in files:
                        full = Path(root) / f
                        z.write(full, arcname=str(full.relative_to(src_dir)))
            return True
        if ext == "tar" or ext == "gz":
            mode = "w:gz" if ext == "gz" else "w"
            with tarfile.open(out_path, mode) as t:
                t.add(src_dir, arcname=".")
            return True
        if ext == "7z":
            seven = shutil.which("7z")
            if not seven:
                return False
            subprocess.run([seven, "a", str(out_path), str(src_dir)], check=True)
            return out_path.exists()
    except Exception:
        return False
    return False
