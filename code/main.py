import os
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk
from owned_cards import display_cards
from reading.read import read_rows, write_rows
from missing import get_new_card_probabilities
from tools import *

path = get_path()

Nb_cartes_Totales = 287
owned = read_rows(path + r'\user\owned.txt')
image_folder = path + r"\Extensions\A1\Boosters"

# Liste pour stocker les références des images, afin de les maintenir en mémoire
global_images_refs = []


def load_booster_image(nom_image):
    """Charge l'image d'un booster et la redimensionne"""
    # Crée le chemin complet vers l'image
    path = os.path.join(image_folder, f"{nom_image}.png")
    
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
        print(f"Error loading image '{nom_image}': {e}")
        return None


def create_main_window():
    root = Tk()
    root.title("Boosters Gallery")
    root.resizable(False, False)  # Désactive le redimensionnement de la fenêtre
    return root


def create_booster_frame(root, booster_data):
    """Crée une frame avec les images de boosters"""
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
    card_count = len(owned)
    Label(root, text=f"Unlocked cards: {card_count} / {total_cards}").pack(pady=10)


def create_buttons(root, on_enter_cards, on_quit):
    """Crée les boutons pour l'interface"""
    Button(root, text="Enter cards", command=on_enter_cards).pack(pady=5)
    Button(root, text="Quit", command=on_quit).pack(pady=5)


def update_owned_cards(root):
    """Met à jour les cartes possédées"""
    global owned
    root.destroy()  # Ferme la fenêtre principale
    owned_cards = display_cards(owned)  # Passe le cache à display_cards
    owned = owned_cards
    main_loop()  # Passe à main_loop


def main_loop():
    """La boucle principale de l'application"""
    global owned
    
    # Créer la fenêtre principale
    root = create_main_window()
    booster_data = get_new_card_probabilities(path, owned)

    # Afficher les images des boosters et leurs pourcentages
    _ = create_booster_frame(root, booster_data)
    
    # Afficher les informations sur les cartes
    display_card_info(root, owned, Nb_cartes_Totales)

    # Définir les actions des boutons
    on_enter_cards = lambda: update_owned_cards(root)
    on_quit = root.destroy
    
    # Créer et afficher les boutons
    create_buttons(root, on_enter_cards, on_quit)
    
    root.mainloop()


# Démarrer la boucle principale
main_loop()

# Sauvegarder les cartes possédées dans le fichier
write_rows(path + r'\user\owned.txt', owned)
