

import os
import tempfile
import ffmpeg


def convert_audio_file(input_file: str, target_format: str) -> str:
    output_file = os.path.join(
        tempfile.gettempdir(),
        os.path.splitext(os.path.basename(input_file))[0] + f".{target_format}"
    )

    (
        ffmpeg
        .input(input_file)
        .output(output_file)
        .run(overwrite_output=True)
    )

    return output_file

