import pypandoc

def convert_text_file(file_path, target_format):
    output_file = f"{file_path}.{target_format}"
    pypandoc.convert_file(file_path, target_format, outputfile=output_file)
    return output_file





