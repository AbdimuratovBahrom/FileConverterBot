import os
import cloudconvert

# Инициализация CloudConvert API
api = cloudconvert.Api(os.getenv("CLOUDCONVERT_API_KEY"))


def cloudconvert_convert(input_file, output_format, output_file=None):
    """
    Конвертация файла через CloudConvert API.
    :param input_file: путь к исходному файлу
    :param output_format: в какой формат конвертировать (например, "docx", "pdf", "mp4")
    :param output_file: путь к выходному файлу (если None, создаётся автоматически)
    :return: путь к выходному файлу
    """
    # Если имя не указано → формируем автоматически
    if output_file is None:
        base, _ = os
