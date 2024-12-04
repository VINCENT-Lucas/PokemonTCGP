import os, requests
from bs4 import BeautifulSoup


''' Returns the "POKEMON TCGP" folder's path, if it's in the exe file you ahve to add the \_internal folder '''
def get_path():
    current_file_path = os.path.abspath(__file__)
    path = os.path.dirname(os.path.dirname(current_file_path))
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
    
def create_directory(path):
    """Crée un répertoire s'il n'existe pas déjà."""
    os.makedirs(path, exist_ok=True)

def fetch_url_content(url):
    """Get and return the html content from an URL"""
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def save_image(url, path):
    """Downloads and save an Image from an URL"""
    if url:
        with requests.get(url, stream=True) as response:
            response.raise_for_status()
            with open(path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)

def get_extension_code(extension_name):
    translate = {"Promo-A": "P-a", "Genetic Apex  (A1)": "A1"}
    return translate[extension_name]

def remove_ex(name):
    ''' Removes the " ex" in the end of a string '''
    if len(name)>3:
        if name[-3:] == " ex":
            return name[:-3]
    return name