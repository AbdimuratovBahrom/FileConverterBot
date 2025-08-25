import os
import cloudconvert

CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

if not CLOUDCONVERT_API_KEY:
    raise RuntimeError("❌ Установите CLOUDCONVERT_API_KEY в .env")

# Создаем клиент
api = cloudconvert.CloudConvert(api_key=CLOUDCONVERT_API_KEY)


async def cloudconvert_convert(input_file: str, output_format: str) -> str:
    """
    Конвертация файлов через CloudConvert API.
    Работает с PDF, аудио, видео и др.
    """
    import tempfile

    # Создаем задачу конвертации
    job = api.jobs.create(payload={
        "tasks": {
            "import-my-file": {
                "operation": "import/upload"
            },
            "convert-my-file": {
                "operation": "convert",
                "input": "import-my-file",
                "output_format": output_format
            },
            "export-my-file": {
                "operation": "export/url",
                "input": "convert-my-file"
            }
        }
    })

    upload_task = job["tasks"][0]

    # Загружаем файл
    with open(input_file, "rb") as f:
        api.tasks.upload(upload_task, f)

    # Ждем завершения
    job = api.jobs.wait(job["id"])
    export_task = next(task for task in job["tasks"] if task["name"] == "export-my-file")

    file_url = export_task["result"]["files"][0]["url"]

    # Скачиваем результат
    output_file = os.path.join(tempfile.gettempdir(), f"converted.{output_format}")
    cloudconvert.download(url=file_url, filename=output_file)

    return output_file
