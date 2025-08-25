import os
import tempfile
from pydub import AudioSegment


def convert_audio_file(input_file: str, target_format: str) -> str:
    output_file = os.path.join(tempfile.gettempdir(),
                               os.path.splitext(os.path.basename(input_file))[0] + f".{target_format}")
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format=target_format)
    return output_file
