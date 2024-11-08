import os
from tkinter import Tk, Label, Button
from PIL import Image, ImageTk

# Chemin du dossier contenant les images
image_files = [f for f in os.listdir('Extensions/A1/cards') if f.endswith('.webp')]
image_files.sort()  # Tri pour afficher les images dans l'ordre (A1, A2, ...)

# Liste pour stocker les cartes "J'ai"
cards_i_have = []

# Index de l'image actuellement affichée
current_index = 0

# Fonction pour afficher l'image suivante
def show_next_image():
    global current_index, image_label
    if current_index < len(image_files):
        # Charge l'image actuelle
        img_path = os.path.join('Extensions/A1/cards', image_files[current_index])
        img = Image.open(img_path)
        img = img.resize((300, 400))  # Redimensionne l'image si nécessaire
        photo = ImageTk.PhotoImage(img)

        # Met à jour l'affichage de l'image
        image_label.config(image=photo)
        image_label.image = photo  # Sauvegarde la référence de l'image pour éviter le garbage collection

# Fonction appelée quand on clique sur "J'ai"
def on_have():
    global current_index
    # Stocke le numéro de la carte (extrait du nom de fichier, sans extension)
    card_number = os.path.splitext(image_files[current_index])[0]
    cards_i_have.append(card_number)
    next_card()

# Fonction appelée quand on clique sur "Non"
def on_not_have():
    next_card()

# Fonction pour passer à l'image suivante
def next_card():
    global current_index
    current_index += 1
    if current_index < len(image_files):
        show_next_image()
    else:
        end_program()

# Fonction pour enregistrer les cartes et quitter
def end_program():
    # Enregistre les cartes sélectionnées dans un fichier texte
    with open("./user/owned.txt", "w") as file:
        file.write("\n".join(cards_i_have))
    print("Cartes 'J'ai' sauvegardées dans cartes_possedees.txt")
    root.quit()

# Initialisation de la fenêtre Tkinter
root = Tk()
root.title("Projet Pokémon")

# Création des widgets d'affichage
image_label = Label(root)
image_label.pack()

# Bouton "J'ai"
have_button = Button(root, text="J'ai", command=on_have)
have_button.pack(side='left', padx=10, pady=10)

# Bouton "Non"
not_have_button = Button(root, text="Non", command=on_not_have)
not_have_button.pack(side='left', padx=10, pady=10)

# Bouton "Terminé"
done_button = Button(root, text="Terminé", command=end_program)
done_button.pack(side='right', padx=10, pady=10)

# Affichage de la première image
show_next_image()

# Lancement de la boucle Tkinter
root.mainloop()
