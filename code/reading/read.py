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

def write_json(dictionnary, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(dictionnary, f, indent=4)

def read_rows(filename):
    data = []
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            data.append(int(line.strip()))
    return data

def write_rows(filename, data):
    with open(filename, "w") as file:
            for card_id in data:
                file.write(str(card_id) + '\n')
