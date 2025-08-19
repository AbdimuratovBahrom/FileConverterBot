from wand.image import Image

def convert_svg_file(file_path, target_format):
    output_file = f"{file_path}.{target_format}"
    with Image(filename=file_path) as img:
        img.format = target_format.upper()
        img.save(filename=output_file)
    return output_file
