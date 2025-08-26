import os
import cloudconvert

cloudconvert.configure(api_key=os.getenv("CLOUDCONVERT_API_KEY"))


def cloudconvert_convert(input_file_url, input_format, output_format, output_file):
    job = cloudconvert.Job.create(payload={
        "tasks": {
            "import-my-file": {
                "operation": "import/url",
                "url": input_file_url
            },
            "convert-my-file": {
                "operation": "convert",
                "input_format": input_format,
                "output_format": output_format,
                "engine": "office",
                "input": ["import-my-file"]
            },
            "export-my-file": {
                "operation": "export/url",
                "input": ["convert-my-file"]
            }
        }
    })

    job = cloudconvert.Job.wait(id=job["id"])  # ждём выполнения

    file = job["tasks"][-1]["result"]["files"][0]  # получаем ссылку
    cloudconvert.download(filename=output_file, url=file["url"])

    return output_file
