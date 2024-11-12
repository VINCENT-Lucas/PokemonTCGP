import os
from tkinter import Tk, Canvas, Frame, Label, Scrollbar, VERTICAL, Button
from PIL import Image, ImageTk, ImageOps

current_file_path = os.path.abspath(__file__)
path = os.path.dirname(os.path.dirname(current_file_path))
print(current_file_path)
if current_file_path.find("_internal") != -1:
    path = path + r"\_internal"
image_folder = path + r"\Extensions\A1\cards"

# Paramètres de dimensionnement
image_width, image_height = 100, 140  # Taille des images après redimensionnement
grid_columns = 5                      # Nombre de colonnes dans la grille
padding = 10                          # Espace autour des images
scrollbar_width = 20                  # Largeur estimée de la Scrollbar

# Chargement et traitement des images
def charger_image(path, griser=False):
    img = Image.open(path).resize((image_width, image_height))
    if griser:
        img = ImageOps.grayscale(img)
    return ImageTk.PhotoImage(img)

# Action sur clic d'une carte pour griser ou dégriser
def toggle_card(card_id, label, img_path, owned_cards, images_refs):
    if card_id in owned_cards:
        owned_cards.remove(card_id)
        img = charger_image(img_path, griser=True)
    else:
        owned_cards.append(card_id)
        img = charger_image(img_path, griser=False)
    
    # Mettre à jour l'image dans le label
    label.config(image=img)
    label.image = img  # Garder une référence pour éviter le garbage collection
    images_refs[card_id] = img  # Mise à jour dans la liste de références

# Création de la grille d'images
def afficher_grille(frame, image_files, owned_cards):
    row, col = 0, 0
    images_refs = {}
    
    for image_file in image_files:
        card_id = int(os.path.splitext(image_file)[0])
        img_path = os.path.join(image_folder, image_file)
        img = charger_image(img_path, griser=(card_id not in owned_cards))
        
        images_refs[card_id] = img  # Sauvegarde pour éviter le garbage collection
        
        # Création du label et assignation de l'événement clic
        label = Label(frame, image=img)
        label.grid(row=row, column=col, padx=padding//2, pady=padding//2)
        label.bind("<Button-1>", lambda event, cid=card_id, lbl=label, path=img_path: 
                   toggle_card(cid, lbl, path, owned_cards, images_refs))
        
        col += 1
        if col >= grid_columns:
            col = 0
            row += 1

    return images_refs

# Calcul de la taille optimale de la fenêtre
def calculer_dimensions_fenetre():
    width = grid_columns * (image_width + padding) + 2 * padding + scrollbar_width
    height = 600  # Hauteur fixe avec scroll pour ajuster dynamiquement
    return width, height

# Initialisation de l'interface avec barre de défilement
def creer_interface():
    window_width, window_height = calculer_dimensions_fenetre()
    root = Tk()
    root.title("Pokemon cards galery")
    root.geometry(f"{window_width}x{window_height}")
    
    canvas = Canvas(root, width=window_width - scrollbar_width, height=window_height)
    canvas.pack(side="left", fill="both", expand=True)
    
    scrollbar = Scrollbar(root, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.config(yscrollcommand=scrollbar.set)
    
    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")
    
    return root, canvas, frame

# Fonction pour gérer le défilement avec la molette de la souris
def on_mousewheel(event, canvas):
    canvas.yview_scroll(int(-3 * (event.delta / 120)), "units")

# Fonction principale
def display(owned_cards):
    image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.webp')])
    root, canvas, frame = creer_interface()
    
    images_refs = afficher_grille(frame, image_files, owned_cards)
    
    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas))
    
    # Bouton "Terminé"
    def terminer():
        root.quit()  # Quitter l'interface Tkinter
        root.destroy()  # Détruire la fenêtre principale

    bouton_termine = Button(root, text="Terminé", command=terminer)
    bouton_termine.pack(side="bottom", pady=10)

    root.mainloop()
    
    return owned_cards  # Retourner la liste mise à jour après fermeture
