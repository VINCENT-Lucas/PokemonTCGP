from missing import *

kanto_pokemon = [
    "Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata",
    "Raticate", "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu",
    "Sandshrew", "Sandslash", "Nidoran♀", "Nidorina", "Nidoqueen", "Nidoran♂",
    "Nidorino", "Nidoking", "Clefairy", "Clefable", "Vulpix", "Ninetales",
    "Jigglypuff", "Wigglytuff", "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume",
    "Paras", "Parasect", "Venonat", "Venomoth", "Diglett", "Dugtrio", "Meowth",
    "Persian", "Psyduck", "Golduck", "Mankey", "Primeape", "Growlithe", "Arcanine",
    "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam", "Machop",
    "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool",
    "Tentacruel", "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke",
    "Slowbro", "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel",
    "Dewgong", "Grimer", "Muk", "Shellder", "Cloyster", "Gastly", "Haunter",
    "Gengar", "Onix", "Drowzee", "Hypno", "Krabby", "Kingler", "Voltorb",
    "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak", "Hitmonlee",
    "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon",
    "Chansey", "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking",
    "Staryu", "Starmie", "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar",
    "Pinsir", "Tauros", "Magikarp", "Gyarados", "Lapras", "Ditto", "Eevee",
    "Vaporeon", "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar", "Kabuto",
    "Kabutops", "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres", "Dratini",
    "Dragonair", "Dragonite", "Mewtwo"
]


def get_card_info(all_cards_dic, extension, id):
    for card in all_cards_dic[extension]:
        if card["Id"] == int(id):
            return card
    print(f"Couldn't find the card {id} in the extension {extension}")
    return None

def load_missing_by_rarity():
    ''' Returns the list of missing cards in the collection by rarity '''
    all_cards = get_all_cards_data()
    owned_cards = read_json(os.path.join(get_path(), "user", "cards_owned.json"))
    missing_cards = get_missing_cards(all_cards, owned_cards)

    missing_by_rarity = {}
    for extension in missing_cards:
        missing_by_rarity[extension] = {}
        for card_id in missing_cards[extension]:
            card_info = get_card_info(all_cards, extension, card_id)
            rarity = card_info["Rarity"]

            if rarity in missing_by_rarity[extension]:
                missing_by_rarity[extension][rarity].append(card_id)
            else:
                missing_by_rarity[extension][rarity] = [card_id]
    return missing_by_rarity

def get_owned_cards_names(owned_cards, all_cards, keep_ex=False):
    ''' Returns the list of the names of the cards owned, toggle keep_ex to differentiate the ex cards from the regular ones'''
    names_set = set()
    for extension in owned_cards:
            for card_id in owned_cards[extension]:
                if owned_cards[extension][card_id] > 0:
                    card_info = get_card_info(all_cards, extension, card_id)
                    if card_info:
                        if keep_ex:
                            name = card_info["Name"]
                        else:
                            name = remove_ex(card_info["Name"])
                        names_set.add(name)
    return names_set

def missing_kanto_pokemons():
    all_cards = get_all_cards_data()
    owned_cards = read_json(os.path.join(get_path(), "user", "cards_owned.json"))

    kanto = set(kanto_pokemon)
    owned_names = get_owned_cards_names(owned_cards, all_cards)
    return kanto.difference(owned_names)
