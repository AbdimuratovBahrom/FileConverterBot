from PIL import Image

def convert_image_file(file_path, target_format):
    output_file = f"{file_path}.{target_format}"
    img = Image.open(file_path)
    img.save(output_file, target_format.upper())
    return output_file
