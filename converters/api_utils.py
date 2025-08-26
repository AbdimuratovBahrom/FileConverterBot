# converters/api_utils.py
import os
import requests

API_KEY = os.getenv("CLOUDCONVERT_API_KEY")
API_URL = "https://api.cloudconvert.com/v2/jobs"

headers = {"Authorization": f"Bearer {API_KEY}"}

def cloudconvert_convert(input_file: str, output_format: str, output_file=None):
    if output_file is None:
        base, _ = os.path.splitext(input_file)
        output_file = f"{base}.{output_format}"

    payload = {
        "tasks": {
            "import": {"operation": "import/upload"},
            "convert": {
                "operation": "convert",
                "input": "import",
                "output_format": output_format
            },
            "export": {"operation": "export/url", "input": "convert"}
        }
    }

    res = requests.post(API_URL, headers=headers, json=payload)
    job = res.json()["data"]

    task = next(t for t in job["tasks"] if t["name"] == "import")
    upload_url = task["result"]["form"]["url"]
    form = task["result"]["form"]["parameters"]

    with open(input_file, "rb") as f:
        requests.post(upload_url, data=form, files={"file": f})

    # Polling job status
    job_id = job["id"]
    while True:
        res = requests.get(f"{API_URL}/{job_id}", headers=headers)
        job = res.json()["data"]
        export = next(t for t in job["tasks"] if t["name"] == "export")
        if export["status"] == "finished":
            file_url = export["result"]["files"][0]["url"]
            break
        elif export["status"] == "error":
            raise RuntimeError("CloudConvert failed")

    result = requests.get(file_url)
    with open(output_file, "wb") as f:
        f.write(result.content)

    return output_file
