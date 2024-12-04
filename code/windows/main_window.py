import os
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk
from .enter_cards import display_cards
from reading.read import *
from missing import *
from tools import *
import tkinter as tk
from windows.wishlist import *


path = get_path()

image_folder = get_path() + r"\Extensions\A1\Boosters"

# Liste pour stocker les références des images, afin de les maintenir en mémoire
global_images_refs = []


def load_booster_image(image_name):
    """Charge l'image d'un booster et la redimensionne"""
    # Crée le chemin complet vers l'image
    path = os.path.join(image_folder, f"{image_name}.png")
    
    if not os.path.exists(path):  # Vérifie que le fichier existe
        return None
    
    try:
        # Tente de charger l'image
        img = Image.open(path).resize((100, 150))  # Redimensionne l'image
        img_tk = ImageTk.PhotoImage(img)  # Convertit en format Tkinter
        
        # Ajoute l'image à la liste pour qu'elle soit maintenue en mémoire
        global_images_refs.append(img_tk)
        
        return img_tk
    except Exception as e:
        print(f"Error loading image '{image_name}': {e}")
        return None


def create_main_window():
    root = Tk()
    root.title("Boosters Gallery")
    root.resizable(False, False)  # Désactive le redimensionnement de la fenêtre
    return root


def create_booster_frame(root, booster_data):
    """Creates a frame with the boosters' images """
    frame = Frame(root)
    frame.pack(pady=10)

    # Réinitialisation de la liste des images à chaque fois que l'on crée un nouveau frame
    for name, percentage in booster_data.items():
        name = name.split("/")[-1]
        img = load_booster_image(name)  # Charge l'image à partir du disque
        if img is None:
            continue

        subframe = Frame(frame)
        subframe.pack(side="left", padx=10)

        try:
            img_label = Label(subframe, image=img)
            img_label.pack()

            Label(subframe, text=f"{percentage:.2f} %").pack()
        except Exception as e:
            print(f"Error displaying image '{name}': {e}")

    return frame


def display_card_info(root, owned, total_cards):
    """Affiche le nombre de cartes débloquées"""
    card_count = sum(len(sub_dict) for sub_dict in owned.values())
    Label(root, text=f"Unlocked cards: {card_count} / {sum(len(sub_dict) for sub_dict in total_cards.values())}").pack(pady=10)


def create_buttons(root, user_cards):
    """Creates the buttons for the interface"""
    on_enter_cards = lambda: update_owned_cards(root, user_cards)
    on_quit = root.destroy

    Button(root, text="Enter cards", command=on_enter_cards).pack(pady=5)
    Button(root, text="Quit", command=on_quit).pack(pady=5)
    return user_cards


def update_owned_cards(root, user_cards):
    """Updates the owned cards"""
    root.destroy()
    user_cards = display_cards(user_cards)
    main_loop(user_cards)
    

def init_cards_owned():
    path = get_path()
    extensions_path = os.path.join(path, "Extensions")

    json_list = {}
    for dir in os.listdir(extensions_path):
        json_list[dir] = {}
    return json_list


def main_loop(user_cards=None):
    """The main loop for the app"""
    if user_cards is None:
        user_cards = read_json(path + r'\user\cards_owned.json')
    if user_cards == {}:
        user_cards = init_cards_owned()
    
    root = create_main_window()  # Crée la fenêtre principale

    booster_data = get_new_card_probabilities(path, user_cards)

    create_booster_frame(root, booster_data)
    
    display_card_info(root, user_cards, get_all_cards_data())
    user_cards = create_buttons(root, user_cards)

    # Ajouter un bouton 'wishlist' pour afficher la liste des souhaits
    wishlist_button = tk.Button(root, text="Wishlist", command=lambda: show_wishlist(root))
    wishlist_button.pack(side=tk.BOTTOM, pady=20)  # Placer le bouton en bas de la fenêtre principale

    root.mainloop()

    write_json(user_cards, os.path.join(path, 'user', 'cards_owned.json'))


def show_wishlist(root):
    """Fonction pour afficher la fenêtre de la wishlist."""
    # Masquer la fenêtre principale
    root.withdraw()

    # Créer la fenêtre wishlist
    wishlist_window = tk.Toplevel(root)
    wishlist_window.title("Wishlist")
    
    # Lancer la classe PokemonWishlistApp (vous devez la définir si elle ne l'est pas déjà)
    app = PokemonWishlistApp(wishlist_window)  # Passe la fenêtre Toplevel comme parent

    # Lors de la fermeture de la fenêtre wishlist, on réaffiche la fenêtre principale
    wishlist_window.protocol("WM_DELETE_WINDOW", lambda: on_wishlist_close(root, wishlist_window))

    # Vous pouvez ajouter plus de fonctionnalités ou personnaliser l'apparence de la wishlist ici.
    wishlist_window.mainloop()


def on_wishlist_close(root, wishlist_window):
    """Fonction qui se déclenche lors de la fermeture de la fenêtre de wishlist"""
    wishlist_window.destroy()  # Ferme la fenêtre de wishlist
    root.deiconify()  # Réaffiche la fenêtre principale