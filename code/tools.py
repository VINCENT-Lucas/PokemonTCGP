import os


''' Returns the "POKEMON TCGP" folder's path, if it's in the exe file you ahve to add the \_internal folder '''
def get_path():
    current_file_path = os.path.abspath(__file__)
    path = os.path.dirname(os.path.dirname(current_file_path))
    print(current_file_path)
    if current_file_path.find("_internal") != -1:
        path = path + r"\_internal"
    return path

def list_directories(path):
    """Returns a list of directories in the specified path."""
    try:
        return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
    except FileNotFoundError:
        return []
    except PermissionError:
        return []

def list_json_files(path):
    """Returns a list of .json files in the specified directory."""
    try:
        return [file for file in os.listdir(path) if file.endswith('.json') and os.path.isfile(os.path.join(path, file))]
    except FileNotFoundError:
        return []
    except PermissionError:
        print(f"Error: Permission denied for accessing '{path}'.")
        return []