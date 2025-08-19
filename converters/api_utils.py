import os
import requests
import cloudconvert
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("CONVERT_API_KEY")

cloudconvert.configure(api_key=API_KEY)

def cloudconvert_convert(input_file, input_format, output_format):
    job = cloudconvert.Job.create(payload={
        "tasks": {
            "import": {
                "operation": "import/upload"
            },
            "convert": {
                "operation": "convert",
                "input": "import",
                "input_format": input_format,
                "output_format": output_format
            },
            "export": {
                "operation": "export/url",
                "input": "convert"
            }
        }
    })

    upload_task = job["tasks"][0]
    upload_url = upload_task["result"]["form"]["url"]

    with open(input_file, "rb") as f:
        requests.post(upload_url, files={"file": f})

    job = cloudconvert.Job.wait(id=job["id"])
    export_task = [t for t in job["tasks"] if t["name"] == "export"][0]

    file_url = export_task["result"]["files"][0]["url"]
    output_file = f"{input_file}.{output_format}"

    r = requests.get(file_url, stream=True)
    with open(output_file, "wb") as f:
        f.write(r.content)

    return output_file
