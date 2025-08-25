import os
import tempfile
from PIL import Image
import cairosvg


def convert_image_file(input_file: str, target_format: str) -> str:
    output_file = os.path.join(tempfile.gettempdir(),
                               os.path.splitext(os.path.basename(input_file))[0] + f".{target_format}")

    ext = os.path.splitext(input_file)[1].lower()

    if ext == ".svg":
        # svg → png/jpg/webp/pdf
        if target_format in ["png", "jpg", "webp", "pdf"]:
            cairosvg.svg2png(url=input_file, write_to=output_file) if target_format == "png" else None
        else:
            raise ValueError("SVG поддерживает только PNG/JPG/WEBP/PDF")
    else:
        img = Image.open(input_file).convert("RGB")
        img.save(output_file, target_format.upper())

    return output_file
