import tkinter as tk
import webbrowser
from tkinter import messagebox
from PIL import Image, ImageTk


class MainFrame(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Stockez la référence au parent
        self.parent = parent

        # Pour le débogage, affichez la structure de grid
        print("Structure de grid dans MainFrame:")

        # Configure grid layout
        self.grid_rowconfigure(0, weight=0)  # Mot
        self.grid_rowconfigure(1, weight=0)  # Zone d'affichage de la réponse
        self.grid_rowconfigure(2, weight=1)  # Zone d'affichage de l'image Wikipédia
        self.grid_rowconfigure(3, weight=0)  # Bouton Wikipedia
        self.grid_rowconfigure(4, weight=0)  # Autres boutons

        self.grid_columnconfigure(0, weight=1)

        print(f"Grid configurée avec 5 rows: {[self.grid_rowconfigure(i) for i in range(5)]}")

        self.create_widgets()

    def create_widgets(self):
        # Configuration du grid principal
        self.grid_columnconfigure(0, weight=1)
        
        # Zone d'affichage du mot (en haut)
        self.word_label = tk.Label(
            self,
            text="",
            font=("Arial", 48, "bold"),
            bg=self["bg"],
            wraplength=800
        )
        self.word_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # Zone d'affichage de la réponse (au milieu)
        self.response_label = tk.Label(
            self,
            text="",
            font=("Arial", 14),
            bg=self["bg"],
            wraplength=800
        )
        self.response_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        # Frame pour l'image Wikipédia (en bas)
        self.wikipedia_frame = tk.Frame(self, bg=self["bg"])
        self.wikipedia_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.wikipedia_frame.grid_columnconfigure(0, weight=1)
        self.wikipedia_frame.grid_rowconfigure(0, weight=1)

        # Label pour l'image Wikipédia
        self.wikipedia_label = tk.Label(
            self.wikipedia_frame,
            text="",
            bg=self["bg"]
        )
        self.wikipedia_label.grid(row=0, column=0, sticky="nsew")

        # Espace pour le bouton Wikipedia (sera créé dynamiquement)
        self.wiki_button_frame = tk.Frame(self, bg=self.parent.bg_color_main)
        self.wiki_button_frame.grid(row=3, column=0, pady=5)

        # Buttons frame déplacé à row=4
        self.create_buttons_frame()

    def create_buttons_frame(self):
        buttons_frame = tk.Frame(self, bg=self.parent.bg_color_main)
        buttons_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        # Configuration des colonnes pour les boutons
        for i in range(6):  # Nombre de boutons
            buttons_frame.grid_columnconfigure(i, weight=1)

        # Bouton "Taper le mot"
        self.type_button = tk.Button(
            buttons_frame,
            text="Taper le mot",
            image=self.parent.icon_type,
            compound=tk.LEFT if self.parent.icon_type else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.type_word
        )
        self.type_button.grid(row=0, column=0, padx=5, sticky="ew")

        # Bouton "Indice"
        self.hint_button = tk.Button(
            buttons_frame,
            text="Indice",
            image=self.parent.icon_hint,
            compound=tk.LEFT if self.parent.icon_hint else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.give_hint
        )
        self.hint_button.grid(row=0, column=1, padx=5, sticky="ew")

        # Bouton "Afficher le mot"
        self.show_button = tk.Button(
            buttons_frame,
            text="Afficher le mot",
            image=self.parent.icon_show,
            compound=tk.LEFT if self.parent.icon_show else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.show_word
        )
        self.show_button.grid(row=0, column=2, padx=5, sticky="ew")

        # Bouton "Définition"
        self.definition_button = tk.Button(
            buttons_frame,
            text="Définition",
            image=self.parent.icon_definition,
            compound=tk.LEFT if self.parent.icon_definition else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.show_definition
        )
        self.definition_button.grid(row=0, column=3, padx=5, sticky="ew")

        # Bouton "Changer de mot"
        self.change_word_button = tk.Button(
            buttons_frame,
            text="Changer de mot",
            image=self.parent.icon_change,
            compound=tk.LEFT if self.parent.icon_change else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.change_word
        )
        self.change_word_button.grid(row=0, column=4, padx=5, sticky="ew")

        # Bouton Wikipedia
        self.wikipedia_button = tk.Button(
            buttons_frame,
            text="Wikipedia",
            image=self.parent.icon_wikipedia,
            compound=tk.LEFT if self.parent.icon_wikipedia else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.show_wikipedia
        )
        self.wikipedia_button.grid(row=0, column=5, padx=5, sticky="ew")

        # Bouton YouTube
        self.youtube_button = tk.Button(
            buttons_frame,
            text="YouTube",
            image=self.parent.icon_youtube,
            compound=tk.LEFT if self.parent.icon_youtube else None,
            font=("Arial", 12),
            bg=self.parent.bg_color_buttons,
            command=self.parent.open_youtube
        )
        self.youtube_button.grid(row=0, column=6, padx=5, sticky="ew")