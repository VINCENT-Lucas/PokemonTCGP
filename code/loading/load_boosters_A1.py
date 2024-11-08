import re, os, json

# Vérifiez si le fichier existe avant de l'ouvrir


def get_cards_in_booster(booster_name):
    file_path = f'./Extensions/A1/Boosters/{booster_name}.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

            # Utilisation d'une expression régulière pour capturer les IDs
            card_ids = re.findall(r'/cards/A1/(\d+)', html_content)

        # Écriture des IDs dans le fichier de sortie
        with open(file_path, 'w', encoding='utf-8') as f_out:
            for card_id in card_ids:
                f_out.write(card_id + '\n')  # Écrit chaque ID sur une nouvelle ligne
    else:
        print(f"Le fichier {file_path} n'existe pas.")

def associate_probabilities(booster_name):
    pack_proba = {"◊": 6, 'Crown Rare': 0.013+0.053, "☆☆☆": 0.222+0.888, "☆☆":0.050+0.2, "☆":0.321+1.286, "◊◊◊◊": 0.333+1.332, "◊◊◊": 0.357+1.428, "◊◊": 2.571+1.714}
    if booster_name == "Charizard":
        # Proba to get the rare pack times the proba for each card (=5%) times the amount of cards
        rare_packs_proba = 5*0.05*5
        rare_pack_list = [284, 280, 252, 253, 255, 257, 263, 266, 268, 272, 274, 278, 228, 229, 230, 231, 234, 236, 237, 246]
    elif booster_name == "Mewtwo":
        rare_packs_proba = 5.263*0.05*5
        rare_pack_list = [286, 282, 251, 258, 261, 262, 264, 269, 270, 275, 277, 227, 239, 242, 243, 244, 245, 247, 249]
    elif booster_name == "Pikachu":
        rare_packs_proba = 5*0.05*5
        rare_pack_list = [285, 281, 254, 256, 259, 260, 265, 267, 271, 273, 276, 279, 232, 233, 235, 238, 240, 241, 248, 250]
    else:
        print("Mauvais nom de Booster")
        return
    
    with open('Extensions/A1/cards_data.json', 'r', encoding='utf-8') as f:
        all_cards_data = json.load(f)  

    with open(f'Extensions/A1/Boosters/{booster_name}.txt', 'r', encoding='utf-8') as f:
        booster_cards = [int(line.strip()) for line in f if line.strip().isdigit()]
    
    probabilities = {}
    for card_id in booster_cards:
        for card_dic in all_cards_data:
            if card_dic["Id"] == card_id:
                rarity = card_dic["Rarity"]
                proba = pack_proba[rarity]
                proba += rare_packs_proba if card_id in rare_pack_list else 0
                probabilities[card_id] = proba
    
    with open(f'Extensions/A1/Boosters/{booster_name}.json', 'w', encoding='utf-8') as f:
        json.dump(probabilities, f, indent=4)  # 'indent=4' pour un formatage lisible

    print(f"Dictionnaire sauvegardé dans le fichier")

associate_probabilities("Pikachu")
associate_probabilities("Mewtwo")
associate_probabilities("Charizard")