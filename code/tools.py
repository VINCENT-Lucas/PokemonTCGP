import os


''' Returns the folder's path, if it's in the exe file you ahve to add the \_internal folder '''
def get_path():
    current_file_path = os.path.abspath(__file__)
    path = os.path.dirname(os.path.dirname(current_file_path))
    print(current_file_path)
    if current_file_path.find("_internal") != -1:
        path = path + r"\_internal"
    return path