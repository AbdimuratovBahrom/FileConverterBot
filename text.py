# text.py
from pathlib import Path
import shutil
import subprocess
import tempfile
import os

# Prefer pypandoc if available, else try LibreOffice (soffice) for some conversions

def _pypandoc_available():
    try:
        import pypandoc  # type: ignore
        return True
    except Exception:
        return False

def convert_text(src: Path, dst: Path, target_ext: str) -> bool:
    target_ext = target_ext.lstrip(".").lower()
    # try pypandoc first
    if _pypandoc_available():
        try:
            import pypandoc  # type: ignore
            output = str(dst)
            pypandoc.convert_file(str(src), target_ext, outputfile=output, extra_args=["--standalone"])
            return dst.exists()
        except Exception:
            pass

    # fallback to LibreOffice headless (for many office formats)
    soff = shutil.which("soffice") or shutil.which("libreoffice")
    if soff:
        try:
            cmd = [soff, "--headless", "--convert-to", target_ext, "--outdir", str(dst.parent), str(src)]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
            # converted file is <stem>.<target_ext>
            expected = dst.parent / f"{src.stem}.{target_ext}"
            if expected.exists():
                expected.rename(dst)
                return True
        except Exception:
            pass

    # as simple fallback: if src is txt and target is docx -> create minimal docx
    if src.suffix.lower() == ".txt" and target_ext in ("docx","odt"):
        try:
            from docx import Document
            doc = Document()
            with src.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    doc.add_paragraph(line.rstrip("\n"))
            doc.save(str(dst))
            return dst.exists()
        except Exception:
            pass

    # if pdf -> txt using pdftotext if available
    if src.suffix.lower() == ".pdf" and target_ext == "txt":
        pdftotext = shutil.which("pdftotext")
        if pdftotext:
            try:
                subprocess.run([pdftotext, str(src), str(dst)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
                return dst.exists()
            except Exception:
                pass

    return False
