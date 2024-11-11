import os, json, sys

def read_list(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        list_ = [int(num) for num in content.strip("[]").split(",")]
    return list_

def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def read_rows(filename):
    data = []
    ensure_user_directory()
    with open(get_resource_path(filename), "r") as file:
        for line in file:
            data.append(int(line.strip()))
    return data

def write_rows(filename, data):
    ensure_user_directory()
    with open(filename, "w") as file:
            for card_id in data:
                file.write(str(card_id) + '\n')

def get_resource_path(relative_path):
    """Retourne le chemin d'accès correct pour les fichiers inclus avec PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Si l'application tourne sous PyInstaller, on utilise sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        # Sinon, on prend le chemin actuel
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def ensure_user_directory():
    """Assure que le dossier user existe."""
    user_dir = get_resource_path("user")
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)