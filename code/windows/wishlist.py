import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
from PIL import Image, ImageTk, ImageEnhance
from windows.missing_cards import *
from missing import *
from tools import *
import os

def create_wishlist_from_names(names):
    wishlist = []
    all_cards_data = get_all_cards_data()
    for name in names:
        for extension in all_cards_data:
            for card in all_cards_data[extension]:
                if card["Name"] == remove_ex(name):
                    card_id = "0"* (3-len(str(card["Id"]))) +str(card["Id"])
                    card_data = {
                        "Name": card["Name"],
                        "Extension": extension,
                        "Id": card_id,
                        "Image_path": os.path.join(get_path(), "Extensions", extension, "cards", card_id + ".webp")
                    }
                    wishlist.append(card_data)
    return wishlist


def create_Mew_Wishlist():
    missing_names = missing_kanto_pokemons()
    return create_wishlist_from_names(missing_names)

def create_Missing_rarity(rarity):
    # rarities: ◊, ◊◊, ◊◊◊, ◊◊◊◊, ☆, ☆☆, ☆☆☆, Crown Rare
    wishlist = []
    missing_by_rarity = load_missing_by_rarity()
    all_cards_data = get_all_cards_data()
    for extension in missing_by_rarity:
        if rarity in missing_by_rarity[extension]:
            for card_id in missing_by_rarity[extension][rarity]:
                card = next((item for item in all_cards_data[extension] if item["Id"] == card_id), None)
                card_id = "0"* (3-len(str(card_id))) +str(card_id)
                card_data = {
                    "Name": card["Name"],
                    "Extension": extension,
                    "Id": card_id,
                    "Image_path": os.path.join(get_path(), "Extensions", extension, "cards", card_id + ".webp")
                }
                wishlist.append(card_data)
    return wishlist
            

class PokemonWishlistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon Wishlist")
        self.root.geometry("660x700")
        self.root.resizable(False, False)  # Empêche le redimensionnement

        self.root.configure(bg="#f5f5f5")

        self.wishlist_missions = {"[Mew mission]": create_Mew_Wishlist, "[◊ Mission]": lambda: create_Missing_rarity("◊"),
                                  "[◊◊◊◊ Mission]": lambda: create_Missing_rarity("◊◊◊◊"),
                                  "[◊◊ Mission]": lambda: create_Missing_rarity("◊◊"),
                                  "[◊◊◊ Mission]": lambda: create_Missing_rarity("◊◊◊"),
                                  "[☆ Mission]": lambda: create_Missing_rarity("☆"),
                                  "[☆☆ Mission]": lambda: create_Missing_rarity("☆☆"),
                                  "[☆☆☆ Mission]": lambda: create_Missing_rarity("☆☆☆"),
                                  "[👑 Mission]": lambda: create_Missing_rarity("Crown Rare")
                                  }

        self.wishlist = []  # Liste des cartes ajoutées à la wishlist
        self.card_images = {}  # Cache des images pour éviter de les recharger à chaque fois
        self.card_width = 100  # Largeur d'une carte (en pixels)
        self.card_height = 150  # Hauteur d'une carte (en pixels)
        self.cards_per_row = 5  # Nombre de cartes par ligne

        self.init_available_cards()
        
        self.create_title()
        self.create_wishlist_area()
        self.create_add_card_area()
        self.create_bottom_buttons()

    def init_available_cards(self):
        """Initialise la liste des cartes disponibles."""
        self.available_cards = []
        cards_data = get_all_cards_data()
        for extension in cards_data:
            for card_data in cards_data[extension]:
                self.available_cards.append(f"{card_data['Name']} - {extension}#{card_data['Id']}")

    def create_title(self):
        """Crée le titre de la page avec une barre colorée."""
        title_frame = tk.Frame(self.root, bg="#f5f5f5")
        title_frame.pack(pady=10)

        tk.Frame(
            title_frame,
            bg="#ffcb05",  # Couleur jaune
            height=5,
            width=200  # Longueur de la barre
        ).pack(pady=5)

        title_label = tk.Label(
            title_frame, 
            text="Wishlist", 
            font=("Verdana", 24, "bold"), 
            bg="#f5f5f5", 
            fg="#000000"
        )
        title_label.pack()

        # Barre colorée
        tk.Frame(
            title_frame,
            bg="#ffcb05",  # Couleur jaune
            height=5,
            width=200  # Longueur de la barre
        ).pack(pady=5)

    def create_wishlist_area(self):
        """Crée la zone d'affichage des cartes de la wishlist."""
        self.wishlist_frame = tk.Frame(self.root, relief=tk.RIDGE, borderwidth=0, padx=10, pady=10)
        self.wishlist_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        canvas_width = self.cards_per_row * (self.card_width + 10)  # Ajuster la largeur du rectangle pour 5 cartes
        self.canvas = tk.Canvas(
            self.wishlist_frame,
            bg="white",
            scrollregion=(0, 0, canvas_width, 500),
            width=canvas_width,
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.wishlist_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Barre de défilement verticale seulement
        self.canvas.config(yscrollcommand=scrollbar.set)

        self.wishlist_inner_frame = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window((0, 0), window=self.wishlist_inner_frame, anchor="nw")

        # Liaison du scrolling avec la molette
        self.canvas.bind("<MouseWheel>", self.on_mouse_scroll)
        self.wishlist_inner_frame.bind("<MouseWheel>", self.on_mouse_scroll)

    def create_add_card_area(self):
        """Crée la zone d'ajout de cartes avec recherche dynamique."""
        # Frame principale avec un fond gris très clair
        add_card_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f9f9f9")
        add_card_frame.pack(fill=tk.X, padx=20, pady=(0, 10))  # Padding moderne

        # Barre de recherche dynamique avec Entry
        self.search_var = tk.StringVar()

        search_label = tk.Label(
            add_card_frame,
            text="Search a card:",
            font=("Segoe UI", 12),
            bg="#f9f9f9",  # Fond harmonisé avec le frame
            fg="#333333",  # Texte gris foncé pour un style moderne
        )
        search_label.pack(side=tk.LEFT, padx=5)

        self.card_entry = tk.Entry(
            add_card_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 12),
            relief="flat",  # Enlève les bordures
            highlightbackground="#cccccc",  # Ajoute une ligne grise subtile autour
            highlightthickness=1,
            bg="white",
            fg="#000000",
        )
        self.card_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True, pady=5)

        self.card_entry.bind("<Down>", self.move_selection_down)
        self.card_entry.bind("<Up>", self.move_selection_up)
        self.card_entry.bind("<KeyRelease>", self.filter_dropdown_options)
        self.card_entry.bind("<Return>", self.on_enter_key)

        # Conteneur pour placer la liste de suggestions sous l'entrée
        suggestion_frame = tk.Frame(self.root, bg="#f9f9f9")
        suggestion_frame.pack(fill=tk.X, padx=10)  # Place sous le champ d'entrée

        # Liste de suggestions dynamique avec un style modernisé
        self.suggestion_listbox = tk.Listbox(
            suggestion_frame,
            font=("Segoe UI", 12),
            relief="flat",  # Enlève les bordures
            bg="white",
            fg="#000000",
            highlightbackground="#cccccc",  # Ligne grise subtile
            highlightthickness=1,
            selectbackground="#d1d1d1",  # Couleur gris clair pour l'élément sélectionné
            selectforeground="#000000",  # Texte noir pour le focus
            height=4
        )
        self.suggestion_listbox.pack(fill=tk.X, pady=10)
        self.suggestion_listbox.bind("<ButtonRelease-1>", self.select_suggestion)

    def on_enter_key(self, event=None):
        """Ajoute la carte sélectionnée dans la liste déroulante à la wishlist."""
        if self.suggestion_listbox.curselection():
            selected_card = self.suggestion_listbox.get(self.suggestion_listbox.curselection())
            self.add_card_to_wishlist(selected_card)
        else:
            self.add_card_to_wishlist()

    def move_selection_down(self, event):
        """Déplace la sélection vers le bas dans la liste des suggestions."""
        current_selection = self.suggestion_listbox.curselection()
        if current_selection:
            next_index = current_selection[0] + 1
            if next_index < self.suggestion_listbox.size():
                self.suggestion_listbox.selection_clear(0, tk.END)
                self.suggestion_listbox.selection_set(next_index)
                self.suggestion_listbox.activate(next_index)
                self.suggestion_listbox.see(next_index)
        else:
            self.suggestion_listbox.selection_set(0)
            self.suggestion_listbox.see(0)

    def move_selection_up(self, event):
        """Déplace la sélection vers le haut dans la liste des suggestions."""
        current_selection = self.suggestion_listbox.curselection()
        if current_selection:
            prev_index = current_selection[0] - 1
            if prev_index >= 0:
                self.suggestion_listbox.selection_clear(0, tk.END)
                self.suggestion_listbox.selection_set(prev_index)
                self.suggestion_listbox.activate(prev_index)
                self.suggestion_listbox.see(prev_index)
        else:
            self.suggestion_listbox.selection_set(self.suggestion_listbox.size() - 1)
            self.suggestion_listbox.see(self.suggestion_listbox.size() - 1)

    def filter_dropdown_options(self, event=None):
        """Filtre les options de la liste déroulante sans fermer ou bloquer l'édition."""

        if event.keysym in ("Up", "Down"):
            return

        search_text = self.search_var.get().lower()
        filtered_cards = [card for card in self.available_cards if search_text in card.lower()]
        
        # Met à jour les valeurs du menu déroulant en fonction du texte saisi
        self.suggestion_listbox.delete(0, tk.END)  # Vide la Listbox
        for card in filtered_cards:
            self.suggestion_listbox.insert(tk.END, card)

        # Si aucune correspondance, vide la sélection
        if filtered_cards:
            self.suggestion_listbox.selection_set(0)  # Sélectionne la première ligne
        else:
            self.suggestion_listbox.insert(tk.END, "Aucune carte trouvée")

    def select_suggestion(self, event):
        """Sélectionne une suggestion et l'ajoute à la wishlist."""
        if self.suggestion_listbox.curselection():
            selected_card = self.suggestion_listbox.get(self.suggestion_listbox.curselection())
            self.add_card_to_wishlist(selected_card)

    def add_card_to_wishlist(self, selected_card=None):
        """Ajoute une carte à la wishlist et met à jour l'affichage."""
        if selected_card is None:
            selected_card = self.card_entry.get()

        if not selected_card or selected_card not in self.available_cards:
            return

        card_info = selected_card.split(" - ")
        card_extension = card_info[1].split("#")[0]
        card_id = str(card_info[1].split("#")[1])
        card_id = "0" * (3-len(card_id)) + card_id if len(card_id) < 3 else card_id
        card_data = {
            "Name": selected_card,
            "Extension": card_extension,
            "Id": card_id,
            "Image_path": os.path.join(get_path(), "Extensions", card_extension, "cards", card_id + ".webp")  # Supposez un chemin d'image
        }
        self.wishlist.append(card_data)

        # Réinitialiser la barre de recherche
        self.search_var.set("")
        self.card_entry.delete(0, tk.END)

        self.display_wishlist()   

    def display_wishlist(self):
        """Affiche les cartes de la wishlist dans la zone prévue."""
        for widget in self.wishlist_inner_frame.winfo_children():
            widget.destroy()  # Supprime les widgets existants

        for i, card in enumerate(self.wishlist):
            image = self.load_card_image(card["Image_path"])
            if image:
                row = i // self.cards_per_row  # Calculer la rangée
                column = i % self.cards_per_row  # Calculer la colonne
                
                label = tk.Label(self.wishlist_inner_frame, image=image)
                label.image = image  # Référence nécessaire pour conserver l'image
                label.grid(row=row, column=column, padx=5, pady=5)
                
                # Bind un clic sur l'image pour supprimer la carte
                label.bind("<Button-1>", lambda event, index=i: self.remove_card_from_wishlist(index))

        # Mettre à jour la région de défilement
        self.wishlist_inner_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def remove_card_from_wishlist(self, index):
        """Supprime une carte de la wishlist."""
        if 0 <= index < len(self.wishlist):
            del self.wishlist[index]  # Supprime la carte à l'indice donné
            self.display_wishlist()  # Met à jour l'affichage

    def load_card_image(self, image_path):
        """Charge une image de carte et la met en cache."""
        if image_path in self.card_images:
            return self.card_images[image_path]

        try:
            img = Image.open(image_path).resize((self.card_width, self.card_height), Image.ANTIALIAS)
            img_tk = ImageTk.PhotoImage(img)
            self.card_images[image_path] = img_tk
            return img_tk
        except Exception as e:
            print(f"Erreur lors du chargement de l'image {image_path}: {e}")
            return None

    def on_mouse_scroll(self, event):
        """Gère le défilement avec la molette de la souris."""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def create_bottom_buttons(self):
        """Crée les boutons en bas de l'interface pour importer et sauvegarder une wishlist."""
        bottom_button_frame = tk.Frame(self.root, bg="#f5f5f5", pady=10)
        bottom_button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        import_button = tk.Button(
            bottom_button_frame,
            text="Import a Wishlist",
            font=("Segoe UI", 12),
            bg="#FFCB05",
            fg="black",
            relief="flat",
            padx=10,
            pady=10,
            command=self.import_wishlist
        )
        import_button.pack(side=tk.LEFT, padx=15, expand=True)

        import_button = tk.Button(
            bottom_button_frame,
            text="Show recommandations",
            font=("Segoe UI", 12),
            bg="#FFFFFF",
            fg="black",
            relief="flat",
            padx=10,
            pady=10,
            command=self.show_recommandations
        )
        import_button.pack(side=tk.LEFT, padx=15, expand=True)

        save_button = tk.Button(
            bottom_button_frame,
            text="Save the Wishlist",
            font=("Segoe UI", 12),
            bg="#E60012",
            fg="black",
            relief="flat",
            padx=10,
            pady=10,
            command=self.save_wishlist
        )
        save_button.pack(side=tk.RIGHT, padx=15, expand=True)

    def import_wishlist(self):
        """Fonction appelée pour importer une wishlist."""
        wishlist_folder = os.path.join(get_path(), "user", "wishlists")

        # Ouvrir la boîte de dialogue pour choisir un fichier
        file_path = filedialog.askopenfilename(
            initialdir=wishlist_folder,  # Dossier initial
            title="Select a Wishlist File",  # Titre de la boîte de dialogue
            filetypes=[("All Files", "*.*")]  # Types de fichiers autorisés
        )

        if file_path:  # Si un fichier est sélectionné
            filename = os.path.basename(file_path).split(".")[0]
            if filename in self.wishlist_missions:
                wishlist = self.wishlist_missions[filename]()
            else:
                wishlist = read_json(file_path)
            self.wishlist = wishlist
            self.display_wishlist()
        else:
            print("Aucun fichier sélectionné.")
        return

    def show_recommandations(self):
        """Calcule les recommandations et affiche une fenêtre avec les boosters."""
        probabilities = determine_pack_to_open_by_id(self.wishlist)

        # Crée une fenêtre
        window = tk.Toplevel()
        window.title("Boosters recommandations")
        window.geometry(f"520x400") 
        window.resizable(False, False)

        base_path = os.path.join(get_path(), "Extensions")
        booster_images = {}

        if not hasattr(self, "images_list"):
            self.images_list = []  

        for root, dirs, files in os.walk(base_path):
            if os.path.basename(root) == "Boosters":
                folder_name = os.path.basename(os.path.dirname(root))
                for file in files:
                    if file.endswith(".png"):
                        booster_name = f"{folder_name}/{os.path.splitext(file)[0]}"
                        booster_images[booster_name] = os.path.normpath(os.path.join(root, file))

        frame = tk.Frame(window)
        frame.pack(expand=True, fill=tk.BOTH)


        for i, booster_name in enumerate(booster_images.keys()):
            probability = probabilities.get(booster_name, 0)

            img_path = booster_images[booster_name]
            print(f"Chargement de l'image pour {booster_name}: {img_path}")

            img = Image.open(img_path).resize((150, 200), Image.ANTIALIAS)

            if probability == 0:
                enhancer = ImageEnhance.Color(img)
                img = enhancer.enhance(0.0)

            img_tk = ImageTk.PhotoImage(img)

            self.images_list.append(img_tk)

            img_label = tk.Label(frame, image=img_tk)
            img_label.grid(row=0, column=i, padx=10, pady=10)

            prob_text = f"{int(probability)}%" if probability == int(probability) else f"{probability:.2f}%"

            prob_label = tk.Label(frame, text=prob_text, font=("Helvetica", 12, "bold"), fg="white", bg="black", padx=5, pady=5, relief="solid", borderwidth=1)
            prob_label.grid(row=1, column=i, padx=10)

        close_button = tk.Button(window, text="Close", command=window.destroy, font=("Helvetica", 12, "bold"), bg="#ff5733", fg="white", relief="raised", bd=3)
        close_button.pack(side=tk.BOTTOM, pady=20)

        window.mainloop()
        
    def save_wishlist(self):
        """Fonction appelée pour sauvegarder la wishlist."""
        if self.wishlist == []:
            return
        name = simpledialog.askstring("", "Enter a name for the save")
        if name is None:
            return 
        
        save_path = os.path.join(get_path(), "user", "wishlists", name)
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.wishlist, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Save Successful", f"Data successfully saved to:\n{save_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des données : {e}")