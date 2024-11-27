from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import os, requests, json, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tools


def process_set_row(set_row, extensions_path):
    """Traite une ligne du tableau des sets et télécharge les données associées."""
    columns = set_row.find_all('td')
    if not columns:
        return

    code = columns[0].find('span', class_='code annotation').text.strip()
    print("Processing set:", code)

    # Create the directories
    set_directory = os.path.join(extensions_path, code)
    tools.create_directory(os.path.join(set_directory, "cards"))

    # Downloads the icon
    icon = columns[0].find('img', class_='set')['src'] if columns[0].find('img', class_='set') else None
    if icon:
        tools.save_image(icon, os.path.join(set_directory, "icon.webp"))

    # Load cards
    cards_path = os.path.join(set_directory, "cards")
    load_all_cards(code, cards_path)

    # Load or save cards data
    cards_data_path = os.path.join(set_directory, "cards_data.json")
    if not os.path.exists(cards_data_path):
        cards_data = load_all_cards_data(code, set_directory)
        save_json(set_directory, cards_data)
    else:
        print(f"No new data loaded for {code}.")

def load_extensions():
    """Charge toutes les extensions depuis le site et enregistre leurs données localement."""
    url = "https://pocket.limitlesstcg.com/cards"
    extensions_path = os.path.join(tools.get_path(), "Extensions")
    tools.create_directory(extensions_path)

    soup = tools.fetch_url_content(url)
    sets = soup.select('table.sets-table tr')

    for set_row in sets:
        process_set_row(set_row, extensions_path)

            
# ------------------ Properties extraction functions -------------------------
def get_name(soup):
    name_section = soup.find('p', class_='card-text-title')
    return name_section.find('span', class_='card-text-name').text.strip()

def get_type_and_hp(soup):
    name_section = soup.find('p', class_='card-text-title')
    details = name_section.text.split("-")
    type_card = details[1].strip() if len(details) > 1 else "None"
    hp = details[2].strip() if len(details) > 2 else "None"
    return type_card, hp

def get_card_type(soup):
    type_section = soup.find('p', class_='card-text-type')
    return type_section.text.strip() if type_section else "None"

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

def get_amount_of_cards(extension):
    ''' We're using the amount of balises there is, but if some balises are missing it creates a gap '''
    url = os.path.join("https://pocket.limitlesstcg.com/cards/", extension)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        card_grid = soup.find('div', class_='card-search-grid')
        
        if card_grid:
            return len(card_grid.find_all('a'))
        print("Error: 'card-search-grid' div not found.")
        return 0
    print(f"Error: Failed to retrieve the page. Status code: {response.status_code}")
    return 0


''' Extension: the extension's code.
    cards_dir: the directory for the extension's cards '''
def load_all_cards(extension, cards_dir):
    os.makedirs(cards_dir, exist_ok=True)
    total_cards = get_amount_of_cards(extension)
    
    for i in range(1, total_cards + 3):
        card_id = "0" * (3 - len(str(i))) + str(i)
        output_filepath = os.path.join(cards_dir, f"{card_id}.webp")

        if os.path.exists(output_filepath):
            print(f"Image {i} already downloaded, skipping.", end="\r")
            continue
        
        url = f"https://limitlesstcg.nyc3.digitaloceanspaces.com/pocket/{extension}/{extension}_{card_id}_EN.webp"
        response = requests.get(url)

        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(output_filepath)
            print(f"Image {i} downloaded.", end="\r")
        else:
            print(f"Error downloading card {card_id}: {response.status_code}")
    print(f"\nEnd of {extension} download")

def load_data(extension, card_id):
    url = f"https://pocket.limitlesstcg.com/cards/{extension}/{int(card_id)}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error loading {card_id} ({response.status_code})")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    data = {
        "Name": get_name(soup),
        "Id": card_id,
        "Rarity": get_card_print_info(soup)[1],
        "Type": get_type_and_hp(soup)[0],
        "HP": get_type_and_hp(soup)[1],
        "Attacks": get_attacks(soup),
        "Weakness": get_weakness_and_retreat(soup)[0],
        "Retreat": get_weakness_and_retreat(soup)[1],
        "Rule": get_rule(soup),
        "Illustrator": get_illustrator(soup),
        "Pack": get_card_print_info(soup)[2],
        "Extension": extension
    }

    return data

# Fonction pour charger toutes les cartes et les sauvegarder dans un fichier JSON
def load_all_cards_data(extension, extension_path):
    all_cards_data = []
    total_cards = get_amount_of_cards(extension)
    for card_id in range(1, total_cards + 1):
        card_data = load_data(extension, card_id)
        if card_data:
            all_cards_data.append(card_data)
            print(f"Card {card_id} loaded.", end="\r")
        else:
            print(f"Error loading card {card_id}.")
    return all_cards_data

def save_json(series_url, all_cards_data):
    with open(os.path.join(series_url, "cards_data.json"), "w", encoding="utf-8") as file:
        json.dump(all_cards_data, file, ensure_ascii=False, indent=4)
    print("Data saved successfully")
# -------------------------------------------------------------------------------- NOTEBOOK-CELL: CODE

load_extensions()