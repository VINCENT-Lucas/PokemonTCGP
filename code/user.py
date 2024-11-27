from tools import *
from reading.read import *
import os

def get_amount_of_cards():
    ''' Returns the amount of cards for every extension '''
    amount_dic = {}
    path = get_path()
    extensions_path = os.path.join(path, "Extensions")

    json_list = []
    for dir in os.listdir(extensions_path):
        json_list.append(os.path.join(dir, "cards_data.json"))

    for file in json_list:
        dic = read_json(os.path.join(extensions_path, file))
        extension_name = os.path.split(file)[0]
        amount_dic[extension_name] = len(dic)
    return amount_dic

get_amount_of_cards()

