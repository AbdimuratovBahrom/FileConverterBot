import os
import cloudconvert
import tempfile

CLOUDCONVERT_API_KEY = os.getenv("CLOUDCONVERT_API_KEY")
api = cloudconvert.Api(CLOUDCONVERT_API_KEY)


def cloudconvert_convert(input_file: str, target_format: str) -> str:
    output_file = os.path.join(tempfile.gettempdir(),
                               os.path.splitext(os.path.basename(input_file))[0] + f".{target_format}")

    job = api.create_job({
        "tasks": {
            "import-file": {"operation": "import/upload"},
            "convert": {
                "operation": "convert",
                "input": "import-file",
                "output_format": target_format
            },
            "export-file": {"operation": "export/url", "input": "convert"}
        }
    })

    upload_task = job["tasks"][0]
    api.upload(upload_task, input_file)

    job = api.wait(job["id"])
    file_url = job["tasks"][-1]["result"]["files"][0]["url"]

    import requests
    r = requests.get(file_url)
    with open(output_file, "wb") as f:
        f.write(r.content)

    return output_file
