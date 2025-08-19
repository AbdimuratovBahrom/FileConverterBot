# converters/pdf.py
import cairosvg
from pathlib import Path

def convert_pdf_file(input_path: str, output_path: str):
    """
    Конвертация PDF в PNG через cairosvg
    """
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Файл {input_path} не найден")

    cairosvg.svg2png(url=input_path, write_to=output_path)
    return output_path
