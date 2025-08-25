import os
import tempfile
import zipfile
import rarfile
import py7zr


def extract_archive(input_file: str) -> str:
    """
    Извлечение архива в temp-папку.
    Поддержка: zip, rar, 7z
    """
    output_dir = tempfile.mkdtemp(prefix="extract_")

    if input_file.endswith(".zip"):
        with zipfile.ZipFile(input_file, 'r') as z:
            z.extractall(output_dir)
    elif input_file.endswith(".rar"):
        with rarfile.RarFile(input_file, 'r') as r:
            r.extractall(output_dir)
    elif input_file.endswith(".7z"):
        with py7zr.SevenZipFile(input_file, mode='r') as z:
            z.extractall(output_dir)
    else:
        raise ValueError("❌ Неподдерживаемый формат архива!")

    return output_dir


def create_archive(input_dir: str, target_format: str = "zip") -> str:
    """
    Создание архива из папки.
    Поддержка: zip, 7z
    """
    base_name = os.path.basename(input_dir.rstrip("/"))
    output_file = os.path.join(tempfile.gettempdir(), f"{base_name}.{target_format}")

    if target_format == "zip":
        with zipfile.ZipFile(output_file, 'w') as z:
            for root, _, files in os.walk(input_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, input_dir)
                    z.write(full_path, rel_path)
    elif target_format == "7z":
        with py7zr.SevenZipFile(output_file, 'w') as z:
            z.writeall(input_dir, arcname=base_name)
    else:
        raise ValueError("❌ Поддерживаются только zip и 7z для упаковки!")

    return output_file
