import os
from tkinter import Tk, Label, Button, Frame
from PIL import Image, ImageTk
from owned_cards import display
from reading.read import read_rows, write_rows
from missing import get_new_card_probabilities

# Read owned cards and initialize variables
owned = read_rows('user/owned.txt')
write_rows('user/owned.txt', owned)

Nb_cartes_Totales = 287    

# Image folder for boosters
image_folder = "./Extensions/A1/Boosters"

# Load and resize booster images
def charger_image_booster(nom_image):
    path = os.path.join(image_folder, f"{nom_image}.png")
    img = Image.open(path).resize((100, 150))
    return ImageTk.PhotoImage(img)

# Main loop that displays the interface
def main_loop():
    global owned  # Ensure owned is updated globally when modified by display()
    
    # Create and set up the main interface window
    root = Tk()
    root.title("Boosters galery")

    probas_debloquer = get_new_card_probabilities(owned)
    Nb_cartes_debloquees = len(owned)

    # Frame for booster images and percentages
    booster_frame = Frame(root)
    booster_frame.pack(pady=10)

    # Define booster names and probabilities
    boosters = {
        "Pikachu": probas_debloquer["Pikachu"],
        "Mewtwo": probas_debloquer["Mewtwo"],
        "Charizard": probas_debloquer["Charizard"]
    }

    images_refs = []  # Store references to images to prevent garbage collection
    for nom_booster, pourcentage in boosters.items():
        img = charger_image_booster(nom_booster)
        images_refs.append(img)

        # Create sub-frame for each booster image and percentage
        booster_subframe = Frame(booster_frame)
        booster_subframe.pack(side="left", padx=10)

        img_label = Label(booster_subframe, image=img)
        img_label.pack()

        pourcentage_label = Label(booster_subframe, text=f"{pourcentage:.2f} %")
        pourcentage_label.pack()

    # Display the number of unlocked cards
    cartes_label = Label(root, text=f"Unlocked cards : {Nb_cartes_debloquees} / {Nb_cartes_Totales}")
    cartes_label.pack(pady=10)

    # Function for "Entrer des cartes" button
    def entrer_cartes():
        global owned
        root.destroy()  # Close the main window
        owned = display(owned)  # Call display and update owned list
        main_loop()  # Restart the main interface after updating cards

    # Button to enter cards
    entrer_btn = Button(root, text="Enter cards", command=entrer_cartes)
    entrer_btn.pack(pady=5)

    # Quit button to exit the loop
    quitter_btn = Button(root, text="Quit", command=root.destroy)
    quitter_btn.pack(pady=5)

    # Run the main interface loop
    root.mainloop()

# Start the main loop
main_loop()
