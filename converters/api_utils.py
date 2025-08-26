import os
import cloudconvert

api = cloudconvert.Api(os.getenv("CLOUDCONVERT_API_KEY"))


def cloudconvert_convert(input_file_url, input_format, output_format, output_file):
    job = api.create_job({
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
                "input": ["convert-my-file"],
                "archive_multiple_files": False
            }
        }
    })

    job = api.wait(job["id"])
    file = job["tasks"][-1]["result"]["files"][0]
    api.download(file, output_file)

    return output_file
