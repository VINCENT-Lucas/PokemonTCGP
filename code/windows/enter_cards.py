import os, json
from tools import *
from tkinter import Tk, Canvas, Frame, Label, Scrollbar, VERTICAL, Button, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import time

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

def create_interface(owned_cards):
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

    # Create a button frame at the bottom
    button_frame = Frame(root, bg="#f5f5f5")
    button_frame.pack(side="bottom", fill="x", pady=10)  # Vertical padding for the entire frame

    # Centering buttons in a sub-container
    button_container = Frame(button_frame, bg="#f5f5f5")
    button_container.pack()

    # Create buttons
    done_button = Button(button_container, text="Done", command=lambda: finish(root), height=20)
    done_button.pack(side="left", padx=10, ipady=10)  # Horizontal padding between buttons

    save_button = Button(button_container, text="Save data", command=lambda: save_data_to_json(owned_cards), height=20)
    save_button.pack(side="left", padx=10, ipady=10)

    return root, canvas, frame


def on_mousewheel(event, canvas):
    canvas.yview_scroll(int(-3 * (event.delta / 120)), "units")


def toggle_card(card_id, canvas, img_path, owned_cards, extension_name, increment):
    """Bascule l'état d'une carte entre possédée et non possédée."""
    current_count = owned_cards[extension_name].get(card_id, 0)
    new_count = current_count + 1 if increment else max(0, current_count - 1)

    if new_count == 0:
        del owned_cards[extension_name][card_id]
    else:
        owned_cards[extension_name][card_id] = new_count

    # Charger une nouvelle image grisée ou normale
    grayscale = new_count == 0
    new_img = load_image(img_path, grayscale=grayscale)

    # Mettre à jour l'image dans le Canvas
    canvas.itemconfig("card_image", image=new_img)
    canvas.image = new_img  # Prévenir le garbage collector

    # Mettre à jour le texte du compteur
    if new_count > 0:
        # Mettre à jour le rectangle et le texte
        canvas.itemconfig("card_text", text=f"x{new_count}")
    else:
        # Supprimer le texte si aucune carte n'est possédée
        canvas.itemconfig("card_text", text="")


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

        # Déterminer si la carte est grisée ou non
        grayscale = card_id not in owned_cards[extension_name] or owned_cards[extension_name][card_id] == 0
        img = load_image(img_path, grayscale=grayscale)

        # Créer un Canvas pour afficher l'image et le texte
        canvas = Canvas(grid_frame, width=image_width, height=image_height, bg="#333333", highlightthickness=0)
        canvas.grid(row=row, column=col, padx=padding // 2, pady=padding // 2)

        # Ajouter l'image au canvas
        canvas.create_image(0, 0, anchor="nw", image=img, tags="card_image")

        # Afficher le compteur si la carte est possédée
        card_count = owned_cards[extension_name].get(card_id, 0)
        if card_count > 0:
            txt = f"x{card_count}"
        else: 
            txt = ""

        # Fond noir pour le texte
        canvas.create_rectangle(
        5, image_height - 25, 45, image_height - 5,  # Coordonnées du rectangle
        fill="#444444",  # Gris foncé pour le remplissage
        outline="#555555",  # Gris légèrement plus clair pour la bordure
        width=2,  # Épaisseur de la bordure
        tags="card_bg"
        )
        # Texte avec le compteur
        canvas.create_text(
            10, image_height - 15,  # Position du texte
            anchor="w", text=txt, fill="white", font=("Arial", 12, "bold"), tags="card_text"
        )

        # Lier les événements de clic gauche et droit
        canvas.bind("<Button-1>", lambda event, cid=card_id, cnv=canvas, path=img_path: 
                    toggle_card(cid, cnv, path, owned_cards, extension_name, increment=True))
        canvas.bind("<Button-3>", lambda event, cid=card_id, cnv=canvas, path=img_path: 
                    toggle_card(cid, cnv, path, owned_cards, extension_name, increment=False))

        col += 1
        if col >= grid_columns:
            col = 0
            row += 1

        global_images.append(img)

def save_data_to_json(owned_cards):
    """Sauvegarde le dictionnaire owned_cards dans un fichier JSON."""

    name = simpledialog.askstring("", "Enter a name for the save")
    if name is None:
        return 
    date = time.strftime("%Y%m%d")
    save_path = os.path.join(get_path(), "user", "saves", name + "_" + str(date))
    try:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(owned_cards, f, indent=4, ensure_ascii=False)
        messagebox.showinfo("Save Successful", f"Data successfully saved to:\n{save_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des données : {e}")

def display_cards(owned_cards):
    """Affiche les cartes et met à jour le dictionnaire owned_cards."""
    reset_cache()
    root, canvas, frame = create_interface(owned_cards)

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

    root.mainloop()

    return owned_cards

def finish(root):    
    root.quit()
    root.destroy()
