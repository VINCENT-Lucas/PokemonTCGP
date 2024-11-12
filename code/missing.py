import os, json
from reading.read import *


def get_new_card_probabilities(path, owned=None):
    with open(path + r'\Extensions\A1\cards_data.json', 'r', encoding='utf-8') as f:
            all_cards_data = json.load(f)

    if owned is None:
        owned = read_rows(path +r'\user\owned.txt')

    missing_cards = []
    for card in all_cards_data:
        if card['Id'] not in owned:
            missing_cards.append(card['Id'])

    # Pour chaque Booster, regarder quelles sont les probas d'obtenir chaque carte, puis afficher les sommes et moyennes des probas
    boosters_list = ["Pikachu", "Charizard", "Mewtwo"]
    stats = {}
    for booster_name in boosters_list:
        with open(path + f'\\Extensions\\A1\\Boosters\\{booster_name}.json', 'r', encoding='utf-8') as f:
            booster_probabilities = json.load(f)
        
        sum_probas = 0
        missing_probabilities = {}
        for id in booster_probabilities:
            sum_probas += booster_probabilities[id]
            if int(id) in missing_cards:
                missing_probabilities[id] = booster_probabilities[id]
        
        proba = 100*sum(missing_probabilities.values())/sum_probas
        stats[booster_name] = proba
        print(f"New card probability for {booster_name} pack: {proba:.2f}%\n")
    return stats