import os
from tkinter import Tk, Canvas, Frame, Label, Scrollbar, VERTICAL, Button
from PIL import Image, ImageTk, ImageOps

# Paths and configurations
def get_extensions_folder():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "_internal" in base_path:
        base_path = os.path.join(base_path, "_internal")
    return os.path.join(base_path, "Extensions")

extensions_path = get_extensions_folder()
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

def toggle_card(card_id, label, img_path, owned_cards, extension_name):
    """Toggle the card's ownership and update the image."""
    # Construire la clé unique basée sur l'extension et l'ID de la carte
    if card_id in owned_cards:
        owned_cards.remove(card_id)
        img = load_image(img_path, grayscale=True)
    else:
        owned_cards.append(card_id)
        img = load_image(img_path, grayscale=False)
    
    # Update the label with the new image
    label.config(image=img)
    label.image = img  # Keep reference to image to avoid garbage collection

    # Storing the image globally to avoid garbage collection
    global_images.append(img)  # Store in the global_images list

def create_image_grid(frame, image_files, image_folder, owned_cards, extension_name):
    """Create a grid of images within the specified frame for the given images."""
    row, col = 0, 0
    grid_frame = Frame(frame)  # Nouveau sous-Frame pour la grille de chaque extension
    grid_frame.pack(anchor="w", padx=padding, pady=padding)  # Utilisation de pack pour positionner le sous-Frame
    
    for image_file in image_files:
        card_id = int(os.path.splitext(image_file)[0])  # ID de la carte
        img_path = os.path.join(image_folder, image_file)

        # Charger l'image depuis le fichier
        img = load_image(img_path, grayscale=(card_id not in owned_cards))

        label = Label(grid_frame, image=img)
        label.grid(row=row, column=col, padx=padding // 2, pady=padding // 2)  # Utilisation de grid pour créer la grille
        label.image = img  # Garder une référence explicite à l'image pour éviter la collecte par le GC
        label.bind("<Button-1>", lambda event, cid=card_id, lbl=label, path=img_path: 
                   toggle_card(cid, lbl, path, owned_cards, extension_name))

        col += 1
        if col >= grid_columns:
            col = 0
            row += 1

        # Stocker l'image dans la liste globale pour éviter qu'elle soit collectée
        global_images.append(img)

def display_cards(owned_cards):
    """Affiche les cartes en utilisant un cache d'images passé en paramètre."""
    # Load images from each extension and organize by extension
    reset_cache()
    root, canvas, frame = create_interface()

    for extension_folder in os.listdir(extensions_path):
        extension_path = os.path.join(extensions_path, extension_folder)
        image_folder = get_image_folder(extension_folder)
        
        if os.path.isdir(image_folder):
            # Load icon and display extension title
            icon_image = load_extension_icon(extension_path)
            global_images.append(icon_image)

            display_extension_title(frame, extension_folder, icon_image)
            
            # Load and display images for this extension
            image_files = sorted([f for f in os.listdir(image_folder) if f.endswith('.webp')])
            create_image_grid(frame, image_files, image_folder, owned_cards, extension_folder)  # Pass extension name here

    frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(event, canvas))

    finish_button = Button(root, text="Finish", command=lambda: finish(root))
    finish_button.pack(side="bottom", pady=10)

    root.mainloop()
    
    return owned_cards

def finish(root):
    # This function will be called to quit the interface
    root.quit()
    root.destroy()
