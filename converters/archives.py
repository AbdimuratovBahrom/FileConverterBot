import os
import tempfile
import zipfile
import rarfile
import py7zr


def extract_archive(input_file: str) -> str:
    out_dir = tempfile.mkdtemp()

    if input_file.endswith(".zip"):
        with zipfile.ZipFile(input_file, "r") as zip_ref:
            zip_ref.extractall(out_dir)

    elif input_file.endswith(".rar"):
        with rarfile.RarFile(input_file) as rar_ref:
            rar_ref.extractall(out_dir)

    elif input_file.endswith(".7z"):
        with py7zr.SevenZipFile(input_file, "r") as archive:
            archive.extractall(out_dir)

    else:
        raise ValueError("Неподдерживаемый архив")

    return out_dir


def create_archive(input_dir: str, target_format: str = "zip") -> str:
    output_file = os.path.join(tempfile.gettempdir(), f"archive.{target_format}")

    if target_format == "zip":
        with zipfile.ZipFile(output_file, "w") as zip_ref:
            for root, _, files in os.walk(input_dir):
                for file in files:
                    zip_ref.write(os.path.join(root, file), arcname=file)
    else:
        raise ValueError("Поддерживается только ZIP")

    return output_file
