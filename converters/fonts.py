from converters.api_utils import cloudconvert_convert


def convert_font_file(file_path, target_format):
    input_format = file_path.split(".")[-1]
    return cloudconvert_convert(file_path, input_format, target_format)
