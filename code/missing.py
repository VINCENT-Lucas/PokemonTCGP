import os, json
from reading.read import *
from tools import *


def get_all_cards_data(path):
    """Loads the card data from the main JSON file."""
    return read_json(os.path.join(path, 'Extensions', 'A1', 'cards_data.json'))

def get_owned_cards(path, owned=None):
    """Retrieves the list of owned card IDs, either from a file or a provided list."""
    if owned is None:
        return read_rows(os.path.join(path, 'user', 'owned.txt'))
    return owned

def get_missing_cards(all_cards_data, owned):
    """Returns a list of IDs for cards that are not owned."""
    return [card['Id'] for card in all_cards_data if card['Id'] not in owned]

def load_booster_probabilities(path, booster_name):
    """Loads probability data for a specific booster from its JSON file."""
    return read_json(os.path.join(path, 'Extensions', 'A1', 'Boosters', f'{booster_name}.json'))

def calculate_booster_probability(booster_probabilities, missing_cards):
    """Calculates the probability of obtaining a new card for a specific booster."""
    total_probability = sum(booster_probabilities.values())
    missing_probability_sum = sum(prob for card_id, prob in booster_probabilities.items() if int(card_id) in missing_cards)
    return 100 * missing_probability_sum / total_probability if total_probability > 0 else 0

def get_new_card_probabilities(path, owned=None):
    """Calculates and returns the probability of getting a new card for each booster."""
    stats = {}
    all_cards_data = get_all_cards_data(path)
    owned = get_owned_cards(path, owned)
    missing_cards = get_missing_cards(all_cards_data, owned)

    extensions_path = os.path.join(path, 'Extensions')
    extensions = list_directories(extensions_path)

    for extension in extensions:
        boosters_path = os.path.join(extensions_path, extension, 'Boosters')
        boosters = list_json_files(boosters_path)

        for booster_name in boosters:
            booster_name = booster_name[:-5]
            booster_probabilities = load_booster_probabilities(path, booster_name)
            new_card_probability = calculate_booster_probability(booster_probabilities, missing_cards)
            stats[extension + "/" + booster_name] = new_card_probability
    
    return stats
