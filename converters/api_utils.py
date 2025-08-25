import os
import requests

CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")
API_URL = "https://api.cloudconvert.com/v2/jobs"

if not CLOUDCONVERT_API_KEY:
    raise ValueError("❌ Нет CLOUDCONVERT_API_KEY в .env!")

headers = {"Authorization": f"Bearer {CLOUDCONVERT_API_KEY}"}


async def cloudconvert_convert(input_file, input_format, output_format, output_file):
    """
    Конвертация файлов через CloudConvert (универсальный REST API).
    """

    # Создаем задачу
    job_resp = requests.post(
        API_URL,
        headers=headers,
        json={
            "tasks": {
                "import-my-file": {"operation": "import/upload"},
                "convert-my-file": {
                    "operation": "convert",
                    "input": "import-my-file",
                    "input_format": input_format,
                    "output_format": output_format,
                },
                "export-my-file": {
                    "operation": "export/url",
                    "input": "convert-my-file",
                },
            }
        },
    )
    job = job_resp.json()["data"]

    # Загружаем файл
    import_task = next(t for t in job["tasks"] if t["name"] == "import-my-file")
    upload_url = import_task["result"]["form"]["url"]
    form_params = import_task["result"]["form"]["parameters"]

    with open(input_file, "rb") as f:
        files = {"file": f}
        requests.post(upload_url, data=form_params, files=files)

    # Ждем завершения
    while True:
        job_status = requests.get(f"{API_URL}/{job['id']}", headers=headers).json()["data"]
        export_task = next(t for t in job_status["tasks"] if t["name"] == "export-my-file")

        if export_task["status"] == "finished":
            file_url = export_task["result"]["files"][0]["url"]
            break
        elif export_task["status"] == "error":
            raise RuntimeError("❌ Ошибка конвертации через CloudConvert")

    # Скачиваем результат
    r = requests.get(file_url)
    with open(output_file, "wb") as f:
        f.write(r.content)

    return output_file
