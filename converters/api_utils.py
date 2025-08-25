import os
import cloudconvert

CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")

# создаём клиент
api = cloudconvert.ApiClient(api_key=CLOUDCONVERT_API_KEY)

async def cloudconvert_convert(input_file, input_format, output_format, output_file):
    """
    Конвертация через CloudConvert (тяжёлые форматы: pdf, видео, аудио).
    """
    if not CLOUDCONVERT_API_KEY:
        raise ValueError("❌ Нет CLOUDCONVERT_API_KEY в .env!")

    job = api.jobs.create(payload={
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

    # загружаем файл
    upload_task = job["tasks"][0]
    upload_url = upload_task["result"]["form"]["url"]
    form_data = upload_task["result"]["form"]["parameters"]

    with open(input_file, "rb") as f:
        cloudconvert.Task.upload(file=f, task=upload_task["id"], api_client=api)

    # ждём завершения
    job = api.jobs.wait(job["id"])

    # получаем ссылку на скачивание
    export_task = [t for t in job["tasks"] if t["name"] == "export-my-file"][0]
    file_url = export_task["result"]["files"][0]["url"]

    # сохраняем результат
    import requests
    r = requests.get(file_url)
    with open(output_file, "wb") as f:
        f.write(r.content)

    return output_file
