# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
import pandas as pd, numpy as np
import requests
from PIL import Image
from io import BytesIO
import os
import requests
from bs4 import BeautifulSoup
import json


# ------------------ Fonctions d'extraction individuelles -------------------------
def get_name(soup):
    name_section = soup.find('p', class_='card-text-title')
    return name_section.find('span', class_='card-text-name').text.strip()

def get_type_and_hp(soup):
    name_section = soup.find('p', class_='card-text-title')
    details = name_section.text.split("-")
    type_card = details[1].strip() if len(details) > 1 else "Type inconnu"
    hp = details[2].strip() if len(details) > 2 else "HP inconnu"
    return type_card, hp

def get_card_type(soup):
    type_section = soup.find('p', class_='card-text-type')
    return type_section.text.strip() if type_section else "Type inconnu"

def get_attacks(soup):
    attacks = []
    attack_sections = soup.find_all('div', class_='card-text-attack')
    for attack in attack_sections:
        attack_info = attack.find('p', class_='card-text-attack-info').text.strip()
        attack_effect = attack.find('p', class_='card-text-attack-effect').text.strip()
        attack_info = ' '.join(attack_info.split())
        symbol = 'GC' if 'GC' in attack_info else ''
        if symbol:
            attack_info = attack_info.replace('GC', '').strip()
        attacks.append({
            'symbol': symbol,
            'info': attack_info,
            'effect': attack_effect
        })
    return attacks

def get_weakness_and_retreat(soup):
    weaknesses_retrait_section_elem = soup.find('p', class_='card-text-wrr')
    if weaknesses_retrait_section_elem:
        weakness_retreat_list = weaknesses_retrait_section_elem.text.split("\n")
        weakness = weakness_retreat_list[1].strip() if len(weakness_retreat_list) > 1 else "None"
        retreat = weakness_retreat_list[2].strip() if len(weakness_retreat_list) > 2 else "None"
    else:
        weakness, retreat = "None", "None"
    return weakness, retreat

def get_rule(soup):
    rule_sections = soup.find_all('p', class_='card-text-wrr')
    return rule_sections[1].text.strip() if len(rule_sections) > 1 else "None"

def get_card_print_info(soup):
    card_prints_section = soup.find('div', class_='card-prints-current')
    if card_prints_section:
        spans = card_prints_section.find_all('span')
        extension = spans[0].text.strip() if len(spans) > 0 else "None"
        if len(spans) > 1:
            card_print_details = spans[1].text.strip()
            print_info = card_print_details.split('·')
            rarity = print_info[1].strip() if len(print_info) > 1 else "None"
            pack = print_info[2].strip() if len(print_info) > 2 else "None"
        else:
            rarity, pack = "None", "None"
    else:
        extension, rarity, pack = "None", "None", "None"
    return extension, rarity, pack

def get_illustrator(soup):
    artist_section = soup.find('div', class_='card-text-section card-text-artist')
    return artist_section.find('a').text.strip() if artist_section else "None"
# ------------------ ------------------------- -------------------------

def load_all_cards():
    output_folder = "Cards"
    os.makedirs(output_folder, exist_ok=True)
    for i in range(1, 287):
        cardID = "0" * (3-len(str(i))) + str(i)
        url = f"https://limitlesstcg.nyc3.digitaloceanspaces.com/pocket/A1/A1_{cardID}_EN.webp"
        output_filename = f"{cardID}.webp"  # Utilise l'extension .webp pour le format d'origine
        response = requests.get(url)

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(os.path.join(output_folder, output_filename))
            print(f"Image {i} ok", end="\r")
        else:
            print(f"Erreur carte {cardID}")

def load_data(card_id):
    url = f"https://pocket.limitlesstcg.com/cards/A1/{int(card_id)}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erreur chargement {card_id}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extraire les informations individuelles
    name = get_name(soup)
    type_card, hp = get_type_and_hp(soup)
    card_type = get_card_type(soup)
    attacks = get_attacks(soup)
    weakness, retreat = get_weakness_and_retreat(soup)
    rule = get_rule(soup)
    extension, rarity, pack = get_card_print_info(soup)
    illustrator = get_illustrator(soup)

    # Organiser les données extraites dans un dictionnaire
    data = {
        "Name": name,
        "Id": card_id,
        "Rarity": rarity,
        "Type": type_card,
        "HP": hp,
        "Attacks": attacks,
        "Weakness": weakness,
        "Retreat": retreat,
        "Rule": rule,
        "Illustrator": illustrator,
        "Pack": pack,
        "Extension": extension
    }

    return data

# Fonction pour charger toutes les cartes et les sauvegarder dans un fichier JSON
def load_all_cards_data():
    all_cards_data = []
    for card_id in range(1, 288):
        card_data = load_data(card_id)
        if card_data:
            all_cards_data.append(card_data)
            print(f"Carte {card_id} chargée !", end="\r")
        else:
            print(f"Erreur {card_id}.")
    return all_cards_data

def save_json(all_cards_data):
    with open("Extensions/A1/cards_data.json", "w", encoding="utf-8") as fichier:
        json.dump(all_cards_data, fichier, ensure_ascii=False, indent=4)
        
    print("Toutes les données ont été sauvegardées en JSON")
# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE
# Appel de la fonction pour charger et sauvegarder les données
all_cards_data = load_all_cards_data()
save_json(all_cards_data)
