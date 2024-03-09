import tkinter as tk
from tkinter import ttk, filedialog
from text import long_text
from text import texto
from yolomain import ObjectDetection


# Création de l'instance
detection = ObjectDetection()

# Création de la fenêtre principale
root = tk.Tk()
root.title("ThingsDetector")

# Définition de la taille de la fenêtre
root.geometry("900x600")

# Modification de la couleur de fond
root.configure(bg='#767799')

# Création d'un style pour les onglets
style = ttk.Style()

# Définition du style pour les onglets non sélectionnés
style.configure('TNotebook.Tab', background='#4A6984', foreground='black', font=('Arial', '15'))

# Définition du style pour l'onglet sélectionné
style.map('TNotebook.Tab', background=[('selected', 'black')], foreground=[('selected', '#306CBD')])

# Définition du style pour le fond du contrôleur d'onglets
style.configure('TNotebook', background='#767799')

# Ajout du menu principal avec les onglets
tab_control = ttk.Notebook(root, style='TNotebook')
tab1 = ttk.Frame(tab_control)
tab2 = ttk.Frame(tab_control)
tab3 = ttk.Frame(tab_control)
tab4 = ttk.Frame(tab_control)

# Ajout des onglets au contrôleur d'onglets
tab_control.add(tab4, text='Accueil')
tab_control.add(tab1, text='Détection d\'image')
tab_control.add(tab2, text='Détection de vidéo')
tab_control.add(tab3, text='Webcam')

# Placement des onglets en utilisant le gestionnaire de grille
tab_control.grid(row=0, column=0, sticky='nsew')

# Création du widget central
central_widget = tk.Frame(root, bg='#C5DFE6')
central_widget.place(relx=0.5, rely=0.5, anchor='center', width=825, height=475)

# Fonction pour mettre à jour le widget central
def update_central_widget(tab):
    # Supprime tous les widgets du widget central
    for widget in central_widget.winfo_children():
        widget.destroy()

    if tab == 'Accueil':
        label = tk.Label(central_widget, background='#C5DFE6', text=long_text)
        label.pack()
    elif tab == 'Détection d\'image':
        # Ajout du titre
        title = tk.Label(central_widget, background='#C5DFE6', text="Analyse d'image", font=('Arial', '20'))
        title.pack()

        # Ajout de la section de texte
        text_section = tk.Label(central_widget, background='#C5DFE6', text=texto, font=('Arial', '15'))
        text_section.pack()

        # Ajout de la section pour l'URL de l'image
        url_entry = tk.Entry(central_widget, background='#767799', foreground='white')
        url_entry.pack()

        # Fonction pour importer une image
        def import_image():
                file_path = filedialog.askopenfilename()  # Ouvre une boîte de dialogue pour choisir un fichier
                detection.process_input(file_path)  # Analyse l'image
        
        # fonction pour importer tout un dossier d'image 
        def import_folder():
                folder_path = filedialog.askdirectory()  # Ouvre une boîte de dialogue pour choisir un dossier
                detection.process_folder(folder_path)  # Analyse toutes les images dans le dossier

        # Fonction pour lancer la détection
        def launch_detection():
                url = url_entry.get()  # Récupère l'URL de l'entrée
                detection.detect_image_from_url(url)  # Analyse l'image à partir de l'URL

        # Ajout des boutons
        import_button = tk.Button(central_widget, background='#006E6E', foreground='white', text="Importer", command=import_image)
        import_button.pack()

        import_button = tk.Button(central_widget, background='#006E6E', foreground='white', text="Folder", command=import_folder)
        import_button.pack()

        detect_button = tk.Button(central_widget, background='#896EDF', foreground='white', text="Détecter", command=launch_detection)
        detect_button.pack()
    elif tab == 'Détection de vidéo':
        # Ajout du titre
        title = tk.Label(central_widget, background='#C5DFE6', text="Analyse de vidéo", font=('Arial', '20'))
        title.pack()

        # Ajout de la section de texte
        text_section = tk.Label(central_widget, background='#C5DFE6', text="Ajouter l'URL dans la section URL ou cliquer sur importer pour charger une vidéo", font=('Arial', '15'))
        text_section.pack()

        # Ajout de la section pour l'URL de la vidéo
        url_entry = tk.Entry(central_widget, background='#767799', foreground='white')
        url_entry.pack()

        # Fonction pour importer une vidéo
        def import_video():
                file_path = filedialog.askopenfilename()  # Ouvre une boîte de dialogue pour choisir un fichier
                detection(file_path)  # Analyse la vidéo

        # Fonction pour lancer la détection
        def launch_detection():
                url = url_entry.get()  # Récupère l'URL de l'entrée
                detection.detect_streaming_video(url)  # Analyse la vidéo à partir de l'URL

        # Ajout des boutons
        import_button = tk.Button(central_widget, background='#006E6E', foreground='white', text="Importer", command=import_video)
        import_button.pack(side='left')

        detect_button = tk.Button(central_widget, background='#896EDF', foreground='white', text="Détecter", command=launch_detection)
        detect_button.pack(side='right')
    elif tab == 'Webcam':
        # Ajout du titre
        title = tk.Label(central_widget, background='#C5DFE6', text="Analyse par la Webcam", font=('Arial', '20'))
        title.pack()
        # Ajout de la section de texte
        text_section = tk.Label(central_widget, background='#C5DFE6', text="Cliquer sur le bouton analyse par la webcam pour lancer une detection live", font=('Arial', '15'))
        text_section.pack()
            # Fonction pour importer une vidéo apartir le la webcam
        def import_video():
            pass  # Ajoutez ici le code pour charger la vidéo live-webcam

        # Fonction pour lancer la détection
        def launch_detection():
                detection.detect_webcam()  # Lance la détection par webcam
        # Ajout des boutons
        detect_button = tk.Button(central_widget, background='#896EDF', foreground='white', text="Webcam", command=launch_detection)
        detect_button.pack()
    else:
        label = tk.Label(central_widget, text=f"Contenu de l'onglet {tab}")
        label.pack()

# Mise à jour du widget central lors du changement d'onglet
tab_control.bind("<<NotebookTabChanged>>", lambda event: update_central_widget(tab_control.tab(tab_control.select(), "text")))

root.mainloop()
