

import os
import pypandoc
import tempfile


def convert_text_file(input_file: str, target_format: str) -> str:
    output_file = os.path.join(tempfile.gettempdir(),
                               os.path.splitext(os.path.basename(input_file))[0] + f".{target_format}")
    pypandoc.convert_file(input_file, target_format, outputfile=output_file, extra_args=["--standalone"])
    return output_file


