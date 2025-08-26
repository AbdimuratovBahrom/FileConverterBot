import os
import cloudconvert

api = cloudconvert.ApiClient(api_key=os.getenv("CLOUDCONVERT_API_KEY"))


async def cloudconvert_convert(input_file: str, output_file: str):
    """
    Конвертирует файл через CloudConvert (новая API).
    input_file: локальный путь к файлу для загрузки
    output_file: путь для сохранения результата
    """
    job = api.jobs.create(payload={
        "tasks": {
            "upload": {"operation": "import/upload"},
            "convert": {
                "operation": "convert",
                "input": "upload",
                "output_format": output_file.split(".")[-1]
            },
            "export": {"operation": "export/url", "input": "convert"}
        }
    })

    # Загрузка файла
    upload_task = job["tasks"][0]
    upload_url = upload_task["result"]["form"]["url"]

    with open(input_file, "rb") as f:
        api.tasks.upload(upload_task, f)

    # Ждём выполнения
    job = api.jobs.wait(job["id"])

    # Скачиваем результат
    export_task = [t for t in job["tasks"] if t["name"] == "export"][0]
    file_url = export_task["result"]["files"][0]["url"]

    import requests
    r = requests.get(file_url)
    with open(output_file, "wb") as f:
        f.write(r.content)
