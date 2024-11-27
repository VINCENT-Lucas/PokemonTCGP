import os
from tools import *
from tkinter import Tk, Canvas, Frame, Label, Scrollbar, VERTICAL, Button
from PIL import Image, ImageTk, ImageOps

# Sauvegarde
extensions_path = os.path.join(get_path(), "Extensions")
image_width, image_height = 100, 140
grid_columns = 5
padding = 10
scrollbar_width = 20

global_images = []  # This will store all the loaded images

def reset_cache():
    global global_images
    global_images = []  # Reset the list of images

reset_cache()

def get_image_folder(extension):
    return os.path.join(extensions_path, extension, "cards")

def load_image(path, grayscale=False):
    """Load an image and optionally convert it to grayscale"""
    img = Image.open(path).resize((image_width, image_height))
    img = ImageTk.PhotoImage(ImageOps.grayscale(img) if grayscale else img)
    return img

def load_extension_icon(extension_path):
    """Load and return the icon image for an extension, resized to a smaller size."""
    icon_path = os.path.join(extension_path, "icon.webp")
    if os.path.exists(icon_path):
        icon = Image.open(icon_path).resize((60, 40))  # Resize icon
        return ImageTk.PhotoImage(icon)
    return None  

def display_extension_title(frame, extension_name, icon_image):
    """Display the title of an extension with its icon in the specified frame with centered, modern style."""
    title_frame = Frame(frame, bg="#f5f5f5")  # Light gray background
    title_frame.pack(fill="x", pady=(padding, 0))  # Full width with padding
    
    # Center content inside title_frame
    title_frame.grid_columnconfigure(0, weight=1)  # Center in x direction

    title_container = Frame(title_frame, bg="#f5f5f5")
    title_container.grid(row=0, column=0, pady=padding)  # Centered placement

    if icon_image:
        icon_label = Label(title_container, image=icon_image, bg="#f5f5f5")
        icon_label.pack(side="left", padx=(0, padding // 2))

    title_label = Label(title_container, text=extension_name, font=("Arial", 16, "bold"), bg="#f5f5f5", fg="#333333")
    title_label.pack(side="left")

def calculate_window_dimensions():
    width = grid_columns * (image_width + padding) + 2 * padding + scrollbar_width
    height = 600
    return width, height

def create_interface():
    window_width, window_height = calculate_window_dimensions()
    root = Tk()
    root.title("Pokemon Card Gallery")
    root.geometry(f"{window_width}x{window_height}")
    root.resizable(False, False)

    main_frame = Frame(root)
    main_frame.pack(fill="both", expand=True)

    canvas = Canvas(main_frame, width=window_width - scrollbar_width, height=window_height - 50)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(main_frame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.config(yscrollcommand=scrollbar.set)

    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    button_frame = Frame(root)
    button_frame.pack(side="bottom", fill="x")

    finish_button = Button(button_frame, text="Save", command=lambda: finish(root))  # Save button
    finish_button.pack(pady=10)

    return root, canvas, frame

def on_mousewheel(event, canvas):
    canvas.yview_scroll(int(-3 * (event.delta / 120)), "units")

def toggle_card(card_id, label, img_path, owned_cards, extension_name, increment=True):
    """Met à jour l'état d'une carte directement dans le dictionnaire owned_cards."""
    # Initialiser le sous-dictionnaire pour l'extension s'il n'existe pas encore
    if extension_name not in owned_cards:
        owned_cards[extension_name] = {}

    # Accéder ou initialiser le compteur pour l'ID de la carte
    current_count = owned_cards[extension_name].get(card_id, 0)

    # Incrémenter ou décrémenter
    if increment:
        owned_cards[extension_name][card_id] = current_count + 1
    else:
        owned_cards[extension_name][card_id] = max(0, current_count - 1)

    # Supprimer la carte si le compteur est à 0 (optionnel)
    if owned_cards[extension_name][card_id] == 0:
        del owned_cards[extension_name][card_id]
        # Supprimer le sous-dictionnaire si vide
        if not owned_cards[extension_name]:
            del owned_cards[extension_name]

    # Définir l'état visuel (grisé ou non)
    grayscale = card_id not in owned_cards.get(extension_name, {})
    img = load_image(img_path, grayscale=grayscale)
    label.config(image=img)
    label.image = img  # Conserver une référence pour éviter la collecte par GC

    # Afficher le compteur sur l'image
    count_text = f"x{owned_cards[extension_name].get(card_id, 0)}" if not grayscale else ""
    label.config(text=count_text, compound="center", font=("Arial", 12, "bold"), fg="#ffffff")

    # Stocker l'image globalement pour éviter qu'elle soit collectée
    global_images.append(img)

def create_image_grid(frame, image_files, image_folder, owned_cards, extension_name):
    """Créer une grille d'images pour les cartes d'une extension spécifique."""
    row, col = 0, 0
    grid_frame = Frame(frame)
    grid_frame.pack(anchor="w", padx=padding, pady=padding)

    # Initialiser le sous-dictionnaire de l'extension si nécessaire
    if extension_name not in owned_cards:
        owned_cards[extension_name] = {}

    for image_file in image_files:
        card_id = str(int(os.path.splitext(image_file)[0]))  # ID de la carte
        img_path = os.path.join(image_folder, image_file)

        
        # Déterminer si la carte est grisées ou non
        grayscale = card_id not in owned_cards[extension_name] or owned_cards[extension_name][card_id] == 0
        img = load_image(img_path, grayscale=grayscale)

        # Créer le label pour l'image
        label = Label(grid_frame, image=img, text="", compound="center", font=("Arial", 12, "bold"), bg="#333333", fg="#ffffff")
        label.grid(row=row, column=col, padx=padding // 2, pady=padding // 2)
        label.image = img

        # Afficher le compteur si la carte est possédée
        count_text = f"x{owned_cards[extension_name].get(card_id, 0)}" if not grayscale else ""
        label.config(text=count_text)

        # Lier les événements de clic gauche et droit
        label.bind("<Button-1>", lambda event, cid=card_id, lbl=label, path=img_path: 
                   toggle_card(cid, lbl, path, owned_cards, extension_name, increment=True))
        label.bind("<Button-3>", lambda event, cid=card_id, lbl=label, path=img_path: 
                   toggle_card(cid, lbl, path, owned_cards, extension_name, increment=False))

        col += 1
        if col >= grid_columns:
            col = 0
            row += 1

        global_images.append(img)

def display_cards(owned_cards):
    """Affiche les cartes et met à jour le dictionnaire owned_cards."""
    reset_cache()
    root, canvas, frame = create_interface()

    for extension_folder in os.listdir(extensions_path):
        extension_path = os.path.join(extensions_path, extension_folder)
        image_folder = get_image_folder(extension_folder)

        if os.path.isdir(image_folder):
            # Charger l'icône et afficher le titre de l'extension
            icon_image = load_extension_icon(extension_path)
            global_images.append(icon_image)

            display_extension_title(frame, extension_folder, icon_image)

            # Charger et afficher les images de l'extension
            image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.webp')])
            create_image_grid(frame, image_files, image_folder, owned_cards, extension_folder)

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas))

    finish_button = Button(root, text="Finish", command=lambda: finish(root))
    finish_button.pack(side="bottom", pady=10)

    root.mainloop()

    return owned_cards

def finish(root):
    root.quit()
    root.destroy()
