import os
import requests
from cloudconvert.client import Client

CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

if not CLOUDCONVERT_API_KEY:
    raise ValueError("❌ Нет CLOUDCONVERT_API_KEY в .env!")

client = Client(api_key=CLOUDCONVERT_API_KEY)

async def cloudconvert_convert(input_file, input_format, output_format, output_file):
    """
    Конвертация через CloudConvert (pdf, видео, тяжёлые аудио).
    """
    job = client.jobs.create(payload={
        "tasks": {
            "import-my-file": {
                "operation": "import/upload"
            },
            "convert-my-file": {
                "operation": "convert",
                "input": "import-my-file",
                "input_format": input_format,
                "output_format": output_format
            },
            "export-my-file": {
                "operation": "export/url",
                "input": "convert-my-file"
            }
        }
    })

    # Загружаем исходный файл
    upload_task = [t for t in job["tasks"] if t["name"] == "import-my-file"][0]
    with open(input_file, "rb") as f:
        client.tasks.upload(file=f, task=upload_task["id"])

    # Ждём выполнения
    job = client.jobs.wait(job["id"])

    # Скачиваем результат
    export_task = [t for t in job["tasks"] if t["name"] == "export-my-file"][0]
    file_url = export_task["result"]["files"][0]["url"]

    r = requests.get(file_url)
    with open(output_file, "wb") as f:
        f.write(r.content)

    return output_file
