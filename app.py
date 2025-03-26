import io
import tkinter as tk
import random
import re
import os
import webbrowser
import requests
from tkinter import simpledialog, messagebox
from PIL import Image, ImageTk, ImageFile
import json
import time
import sys

# Allow loading truncated/corrupted images
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Import sub-modules
from utils.resource_utils import resource_path
from utils.text_utils import shuffle_preserving_punctuation
from utils.wikipedia_utils import fetch_wikipedia_image, load_gif_animation
from ui.theme_frame import ThemeFrame
from ui.main_frame import MainFrame
from ui.advanced_frame import AdvancedFrame
from ui.bottom_frame import BottomFrame

# TTS est désactivé
TTS_AVAILABLE = False

# Import word dictionary
from words import words

# -- Toggle debugging (True/False) --
DEBUG = True  # Activé pour le débogage

# Chemins des ressources
ICON_PATH = "assets"  # Les icônes sont directement dans le dossier assets
GIF_PATH = "assets"   # Les GIFs sont aussi dans le dossier assets
DATA_PATH = "data"

def debug_log(*args):
    """Displays debug messages if DEBUG is True."""
    if DEBUG:
        print(*args)


class GifAnimator:
    def __init__(self, parent, label):
        self.parent = parent
        self.label = label
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self.animation_id = None
        self.is_playing = False

    def load_gif(self, source):
        try:
            # Nettoyer l'état précédent
            self.stop()
            
            # Ouvrir le GIF
            if isinstance(source, str):
                gif = Image.open(source)
            else:
                source.seek(0)
                gif = Image.open(source)

            if gif.format != 'GIF':
                self.label.config(text="Le fichier n'est pas un GIF")
                return False

            # Redimensionner si nécessaire en conservant les proportions
            max_size = (400, 400)
            original_width, original_height = gif.size
            ratio = min(max_size[0] / original_width, max_size[1] / original_height)
            new_width = int(original_width * ratio)
            new_height = int(original_height * ratio)

            # Lire toutes les frames
            self.frames = []
            self.durations = []
            
            while True:
                frame = gif.copy()
                # Redimensionner la frame en conservant les proportions
                frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame))
                self.durations.append(gif.info.get('duration', 100))
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"DEBUG: Erreur lors du chargement du GIF: {e}")
            self.label.config(text=f"Erreur GIF: {e}")
            return False

        if not self.frames:
            self.label.config(text="Aucune frame trouvée dans le GIF")
            return False

        return True

    def play(self):
        if not self.frames:
            return
        
        self.is_playing = True
        self._show_next_frame()

    def stop(self):
        self.is_playing = False
        if self.animation_id:
            try:
                self.parent.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
        self.frames = []
        self.durations = []
        self.current_frame = 0
        self.label.config(image="", text="")
        self.label.image = None

    def _show_next_frame(self):
        if not self.is_playing or not self.frames:
            return

        try:
            self.label.config(image=self.frames[self.current_frame])
            self.label.image = self.frames[self.current_frame]
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            delay = self.durations[self.current_frame]
            self.animation_id = self.parent.after(delay, self._show_next_frame)
        except Exception as e:
            print(f"DEBUG: Erreur lors de l'animation: {e}")
            self.label.config(text="Erreur d'animation")
            self.stop()


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # Main window configuration
        self.title("AnatoLexic - Apprentissage de l'anatomie humaine")
        self.geometry("1000x750")
        self.minsize(800, 600)

        # Configure grid (4 rows, 1 column)
        self.grid_rowconfigure(1, weight=1)  # Main area should expand
        self.grid_columnconfigure(0, weight=1)

        # --- State variables / Parameters ---
        self.letter_index = 0
        self.shuffled_word = None
        self.current_word = None
        self.current_definition = None
        self.theme_var = tk.StringVar()
        self.subtheme_var = tk.StringVar()
        self.score = 0
        self.total_attempts = 0
        self.flashcard_mode = True
        self.timer_duration = 30
        self.timer_active = False
        self.timer_id = None
        self.displayed_list = []
        self.last_loaded_word = None  # Pour éviter de recharger le même mot

        # Ajout du contrôle pour le timer automatique
        self.auto_timer = False

        # "Theme" colors
        self.bg_color_main = "#F0F0F0"
        self.bg_color_frame = "#E8E8E8"
        self.bg_color_buttons = "#D8D8D8"
        self.fg_color_text = "black"

        self.configure(bg=self.bg_color_main)

        # Load icons / images
        self.background = None
        try:
            background_image = Image.open(resource_path(os.path.join("assets", "anatomy_background.png")))
            self.background = ImageTk.PhotoImage(background_image)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de fond: {e}")
            pass

        # Utility method to load icons
        def _load_image(path):
            """Charge une image avec gestion des erreurs"""
            try:
                # Vérifier si l'application est en mode développement ou compilée
                if getattr(sys, 'frozen', False):
                    # Si l'application est compilée
                    base_path = sys._MEIPASS
                else:
                    # Si l'application est en mode développement
                    base_path = os.path.dirname(os.path.abspath(__file__))
                
                full_path = os.path.join(base_path, path)
                print(f"Tentative de chargement de l'image : {full_path}")
                if os.path.exists(full_path):
                    # Charger l'image PIL
                    pil_image = Image.open(full_path)
                    # Convertir en PhotoImage pour Tkinter
                    return ImageTk.PhotoImage(pil_image)
                else:
                    print(f"Image non trouvée: {full_path}")
                    return None
            except Exception as e:
                print(f"Erreur lors du chargement de l'image {path}: {e}")
                return None

        self.icon_type = _load_image(os.path.join(ICON_PATH, "finger_icon.png"))
        self.icon_show = _load_image(os.path.join(ICON_PATH, "text_icon.png"))
        self.icon_definition = _load_image(os.path.join(ICON_PATH, "book_search_icon.png"))
        self.icon_change = _load_image(os.path.join(ICON_PATH, "refresh_icon.png"))
        self.icon_wikipedia = _load_image(os.path.join(ICON_PATH, "wikipedia_icon.png"))
        self.icon_youtube = _load_image(os.path.join(ICON_PATH, "youtube_icon.png"))
        self.icon_hint = _load_image(os.path.join(ICON_PATH, "lightbulb_icon.png"))
        self.icon_message = _load_image(os.path.join(ICON_PATH, "message_icon.png"))

        self.wikipedia_photo = None

        # Créer l'animateur GIF
        self.gif_animator = None

        # Ajout du contrôle pour le chargement automatique des images
        self.auto_load_images = True

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        """
        Builds the entire interface (4 zones: theme_frame, main_frame, advanced_frame, bottom_frame).
        """

        # ----- (1) Theme / Sub-theme Frame (row=0) -----
        theme_frame = ThemeFrame(
            self,
            self.theme_var,
            self.subtheme_var,
            self.update_subthemes,
            words.keys(),
            bg=self.bg_color_frame,
            bd=2,
            relief=tk.GROOVE
        )
        theme_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # ----- (2) Main Frame (row=1) -----
        main_frame = MainFrame(
            self,
            bg=self.bg_color_main,
            bd=2,
            relief=tk.RIDGE
        )
        main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.main_frame = main_frame

        # Créer l'animateur GIF après la création du main_frame
        self.gif_animator = GifAnimator(self, self.main_frame.wikipedia_label)

        # ----- (3) Advanced Frame (row=2) -----
        advanced_frame = AdvancedFrame(
            self,
            self.flashcard_mode,
            bg=self.bg_color_frame,
            bd=2,
            relief=tk.GROOVE
        )
        advanced_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.advanced_frame = advanced_frame

        # ----- (4) Bottom Frame (row=3) -----
        bottom_frame = BottomFrame(
            self,
            TTS_AVAILABLE,
            bg=self.bg_color_frame,
            bd=2,
            relief=tk.SUNKEN
        )
        bottom_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        self.bottom_frame = bottom_frame

        # Créer un bouton permanent invisible pour maintenir la référence
        self.permanent_wiki_button = tk.Button(self)
        self.permanent_wiki_button.grid_remove()  # Cache le bouton

    def check_word_selected(self):
        """
        Checks if a word is selected, otherwise displays an error.
        Returns True if OK, False if no word.
        """
        if not self.current_word:
            messagebox.showerror("Erreur", "Aucun mot n'est actuellement sélectionné/affiché.")
            return False
        return True

    # -------------- Theme / Sub-theme Management --------------

    def update_subthemes(self, event):
        theme = self.theme_var.get()
        subthemes = list(words[theme].keys()) if theme else []
        if subthemes:
            self.subtheme_var.set(subthemes[0])
            # Correction : accéder au menu dans theme_frame, pas main_frame
            theme_frame_menu = self.children[list(self.children.keys())[0]]  # Premier widget enfant (theme_frame)
            theme_frame_menu.sous_theme_menu["menu"].delete(0, "end")
            for st in subthemes:
                theme_frame_menu.sous_theme_menu["menu"].add_command(
                    label=st,
                    command=lambda val=st: [self.subtheme_var.set(val), self.update_word()]
                )
        self.update_word()

    def update_word(self):
        debug_log("Called update_word()")
        theme = self.theme_var.get()
        subtheme = self.subtheme_var.get()

        # Réinitialiser l'image Wikipédia avant de changer de mot
        self.reset_wikipedia_label()
        self.last_loaded_word = None  # Réinitialiser explicitement le dernier mot chargé

        # Gérer le timer automatique
        if self.timer_active:
            self.toggle_timer()  # Arrêter le timer actuel
        if self.auto_timer:
            self.after(100, self.toggle_timer)  # Redémarrer le timer avec un petit délai

        if theme and subtheme:
            words_in_subtheme = words[theme][subtheme]
            if not words_in_subtheme:
                debug_log("No words in this subtheme.")
                self.current_word = None
                self.current_definition = None
                self.main_frame.word_label.config(
                    text="Aucun mot à afficher.",
                    font=("Arial", 48, "bold")
                )
                return

            # Si le nouveau mot est le même que l'ancien, en choisir un autre
            new_word, new_definition = random.choice(words_in_subtheme)
            while new_word == self.current_word and len(words_in_subtheme) > 1:
                new_word, new_definition = random.choice(words_in_subtheme)

            self.current_word = new_word
            self.current_definition = new_definition
            self.letter_index = 0
            self.main_frame.response_label.config(text="")
            self.displayed_list = []

            if not self.flashcard_mode:
                debug_log(f"[Normal Mode] Selected word: {self.current_word}")
                shuffled_word = shuffle_preserving_punctuation(self.current_word)
                self.displayed_list = list(shuffled_word)
                self.main_frame.word_label.config(
                    text=" ".join(self.displayed_list),
                    font=("Arial", 48, "bold")
                )
            else:
                debug_log(f"[Flashcard Mode] Selected word: {self.current_word}")
                for c in self.current_word:
                    if c == " ":
                        self.displayed_list.append(" ")
                    else:
                        self.displayed_list.append("_")
                self.main_frame.word_label.config(
                    text=" ".join(self.displayed_list),
                    font=("Arial", 48, "bold")
                )
                self.main_frame.response_label.config(text=self.current_definition)
        else:
            debug_log("No theme/subtheme selected.")
            self.current_word = None
            self.current_definition = None
            self.displayed_list = []
            self.main_frame.word_label.config(
                text="",
                font=("Arial", 48, "bold")
            )

    def change_word(self):
        """Change le mot actuel et réinitialise l'état de l'image."""
        self.reset_wikipedia_label()
        self.last_loaded_word = None  # Réinitialiser explicitement le dernier mot chargé
        self.update_word()
        if self.timer_active:
            self.toggle_timer()

    # -------------- Verification / Answers --------------

    def type_word(self):
        if not self.check_word_selected():
            return
        answer = simpledialog.askstring("Taper le mot", "Entrez le mot :")
        if answer:
            self.total_attempts += 1
            self.verify_answer(answer)

    def verify_answer(self, answer):
        if not self.current_word:
            return
        if answer.lower() == self.current_word.lower():
            self.main_frame.response_label.config(text="Bravo, c'est la bonne réponse !", fg="green")
            self.main_frame.word_label.config(text=self.current_word)
            self.score += 1
        else:
            self.main_frame.response_label.config(text=f"Mauvaise réponse.\nLe mot était : {self.current_word}",
                                                  fg="red")
            self.main_frame.word_label.config(text=self.current_word)
        self.update_score()

    def show_word(self):
        if not self.check_word_selected():
            return
            
        # Réinitialiser d'abord le label Wikipédia
        self.reset_wikipedia_label()
        
        # Afficher le mot avec une police beaucoup plus grande
        self.main_frame.word_label.config(
            text=self.current_word,
            font=("Arial", 48, "bold")
        )
        self.update_idletasks()
        
        # Charger l'image seulement si auto_load_images est activé
        if self.auto_load_images:
            self.after(1000, self._load_image_after_delay)

    def _load_image_after_delay(self):
        """Charge l'image Wikipédia après un délai"""
        self.show_wikipedia_image()

    def show_definition(self):
        if not self.check_word_selected():
            return
        if self.current_definition:
            self.main_frame.response_label.config(text=self.current_definition, fg=self.fg_color_text)

    # -------------- Timer --------------

    def toggle_timer(self):
        if not self.timer_active:
            self.timer_active = True
            self.bottom_frame.timer_button.config(text="Arrêter Timer")
            self.timer_duration = 30
            self.update_timer()
        else:
            self.timer_active = False
            self.bottom_frame.timer_button.config(text="Démarrer Timer")
            if self.timer_id:
                self.after_cancel(self.timer_id)
            self.bottom_frame.timer_label.config(text="Temps restant : --")

    def update_timer(self):
        if self.timer_active:
            if self.timer_duration > 0:
                self.bottom_frame.timer_label.config(text=f"Temps restant : {self.timer_duration}s")
                self.timer_duration -= 1
                self.timer_id = self.after(1000, self.update_timer)
            else:
                self.bottom_frame.timer_label.config(text="Temps écoulé !")
                messagebox.showwarning(
                    "Temps écoulé",
                    f"Le temps pour répondre est écoulé.\nMot : {self.current_word}"
                )
                self.main_frame.word_label.config(text=self.current_word)
                self.timer_active = False
                self.bottom_frame.timer_button.config(text="Démarrer Timer")

    # -------------- Flashcard Mode --------------

    def toggle_flashcard_mode(self):
        self.flashcard_mode = not self.flashcard_mode
        if self.flashcard_mode:
            self.advanced_frame.flashcard_button.config(text="Désactiver Mode Flashcard (ON)")
        else:
            self.advanced_frame.flashcard_button.config(text="Activer Mode Flashcard (OFF)")
        self.update_word()

    def suggest_letter(self):
        if not self.check_word_selected():
            return
        if not self.flashcard_mode:
            messagebox.showinfo("Info", "Le mode flashcard n'est pas activé.")
            return

        letter = simpledialog.askstring("Proposer une lettre", "Tapez une lettre :")
        if not letter:
            return
        letter = letter.strip()
        if len(letter) != 1:
            messagebox.showwarning("Attention", "Veuillez taper UNE lettre uniquement.")
            return
        letter = letter.lower()
        word_lower = self.current_word.lower()

        num_revelations = 0
        for i, char in enumerate(self.displayed_list):
            if char == "_":
                if i < len(word_lower) and word_lower[i] == letter:
                    self.displayed_list[i] = self.current_word[i]
                    num_revelations += 1

        self.main_frame.word_label.config(text=" ".join(self.displayed_list))
        
        # Vérifier si le mot est complètement révélé
        displayed_joined = "".join(self.displayed_list).lower().replace(" ", "")
        original_joined = self.current_word.lower().replace(" ", "")
        if displayed_joined == original_joined:
            messagebox.showinfo("Bravo", "Vous avez découvert toutes les lettres du mot !")
            # Charger automatiquement l'image Wikipédia
            self.show_wikipedia_image()
        elif num_revelations == 0:
            messagebox.showinfo("Info", f"La lettre '{letter}' n'apparaît pas dans ce mot.")

    def give_hint(self):
        if not self.check_word_selected():
            return
        if not self.displayed_list:
            messagebox.showinfo("Indice", "Aucune donnée à afficher...")
            return

        displayed_joined = "".join(self.displayed_list).lower().replace(" ", "")
        original_joined = self.current_word.lower().replace(" ", "")

        if displayed_joined == original_joined:
            messagebox.showinfo("Indice", "Le mot est déjà complet !")
            return

        non_matching_indices = []
        for i, char in enumerate(self.displayed_list):
            if char == " ":
                continue
            if i < len(self.current_word) and char.lower() != self.current_word[i].lower():
                non_matching_indices.append(i)

        if not non_matching_indices:
            messagebox.showinfo("Indice", "Toutes les lettres semblent déjà correctes.")
            return

        chosen_index = random.choice(non_matching_indices)
        self.displayed_list[chosen_index] = self.current_word[chosen_index]
        self.main_frame.word_label.config(text=" ".join(self.displayed_list))
        
        # Vérifier si le mot est complètement révélé
        displayed_joined = "".join(self.displayed_list).lower().replace(" ", "")
        original_joined = self.current_word.lower().replace(" ", "")
        if displayed_joined == original_joined:
            # Charger automatiquement l'image Wikipédia
            self.show_wikipedia_image()

    # -------------- Wikipedia / YouTube / Images --------------

    def show_wikipedia(self):
        if not self.check_word_selected():
            return
        search_term = self.current_word.replace(" ", "_")
        url_wikipedia = f"https://fr.wikipedia.org/wiki/{search_term}"
        webbrowser.open(url_wikipedia)

    def open_youtube(self):
        if not self.check_word_selected():
            return
        search_term = self.current_word.replace(" ", "+")
        url_youtube = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.open(url_youtube)

    def show_wikipedia_image(self):
        """Affiche une image depuis Wikipedia pour le mot actuel."""
        if not self.check_word_selected():
            print("DEBUG: Aucun mot sélectionné")
            return

        word = self.current_word
        print(f"DEBUG: Tentative d'afficher une image pour: '{word}'")

        # Vérifier si c'est le même mot que le dernier chargé
        if word == self.last_loaded_word:
            print("DEBUG: Ce mot a déjà été chargé")
            messagebox.showinfo("Information", "L'image de ce mot est déjà chargée.")
            return

        # Désactiver le bouton pendant le chargement
        self.permanent_wiki_button.config(state=tk.DISABLED)
        print("DEBUG: Bouton temporairement désactivé")

        # Effacer l'image précédente
        self.reset_wikipedia_label()
        self.main_frame.wikipedia_label.config(text="Chargement en cours...")
        self.update_idletasks()

        try:
            # Rechercher l'image sur Wikipedia
            success = self.load_wikipedia_image(word)
            
            if success:
                print("DEBUG: Image chargée avec succès")
                self.permanent_wiki_button.config(state=tk.NORMAL)
                self.last_loaded_word = word  # Mettre à jour le dernier mot chargé
            else:
                print("DEBUG: Échec du chargement de l'image")
                self.main_frame.wikipedia_label.config(
                    text="❌ Aucune image disponible pour ce terme.",
                    image=""
                )
                self.permanent_wiki_button.config(state=tk.NORMAL)
                self.last_loaded_word = None  # Réinitialiser le dernier mot chargé en cas d'échec
        except Exception as e:
            print(f"DEBUG: Erreur lors du chargement de l'image: {str(e)}")
            self.main_frame.wikipedia_label.config(
                text="❌ Erreur lors du chargement de l'image.",
                image=""
            )
            self.permanent_wiki_button.config(state=tk.NORMAL)
            self.last_loaded_word = None  # Réinitialiser le dernier mot chargé en cas d'erreur

    def load_wikipedia_image(self, mot):
        headers = {'User-Agent': 'Mozilla/5.0'}
        mot_recherche = mot.replace(" ", "_")
        api_url = "https://fr.wikipedia.org/w/api.php"

        print(f"DEBUG: Recherche d'image pour '{mot}' (recherche: '{mot_recherche}')")

        # Première tentative avec le mot exact
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original",
            "titles": mot_recherche,
            "redirects": 1  # Suivre les redirections
        }

        try:
            print("DEBUG: Envoi de la requête à l'API Wikipédia...")
            r = requests.get(api_url, params=params, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            print("DEBUG: Réponse API reçue")
            pages = data.get("query", {}).get("pages", {})

            # Si aucune page n'est trouvée, essayer une recherche plus large
            if not pages or "-1" in pages:
                print("DEBUG: Aucune page trouvée, tentative de recherche alternative...")
                # Deuxième tentative avec une recherche plus large
                params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": mot_recherche,
                    "srlimit": 1,
                    "srprop": "snippet"
                }
                
                r = requests.get(api_url, params=params, headers=headers, timeout=10)
                r.raise_for_status()
                search_data = r.json()
                
                search_results = search_data.get("query", {}).get("search", [])
                if search_results:
                    # Utiliser le premier résultat de recherche
                    page_title = search_results[0]["title"]
                    print(f"DEBUG: Page trouvée via recherche : {page_title}")
                    
                    # Récupérer l'image pour cette page
                    params = {
                        "action": "query",
                        "format": "json",
                        "prop": "pageimages",
                        "piprop": "original",
                        "titles": page_title,
                        "redirects": 1
                    }
                    
                    r = requests.get(api_url, params=params, headers=headers, timeout=10)
                    r.raise_for_status()
                    data = r.json()
                    pages = data.get("query", {}).get("pages", {})

            if not pages or "-1" in pages:
                print("DEBUG: Aucune page trouvée après recherche alternative")
                return False

            print(f"DEBUG: Nombre de pages trouvées : {len(pages)}")

            for page_id, page_info in pages.items():
                print(f"DEBUG: Examen de la page {page_id}")
                print(f"DEBUG: Informations de la page : {page_info}")
                
                if "original" in page_info:
                    img_url = page_info["original"]["source"]
                    print(f"DEBUG: URL de l'image trouvée : {img_url}")

                    try:
                        print("DEBUG: Téléchargement de l'image...")
                        response = requests.get(img_url, headers=headers, timeout=10)
                        response.raise_for_status()
                        
                        print("DEBUG: Conversion des données en image...")
                        image_data = io.BytesIO(response.content)
                        image = Image.open(image_data)
                        
                        # Vérifier si c'est un GIF
                        if image.format == 'GIF' and getattr(image, 'is_animated', False):
                            print("DEBUG: Image GIF animée détectée")
                            # Utiliser la fonction _load_gif_animation pour les GIFs
                            self._load_gif_animation(image_data, self.main_frame.wikipedia_label)
                            return True
                        else:
                            print("DEBUG: Image statique détectée")
                            try:
                                # Redimensionner l'image si elle est trop grande
                                max_size = (400, 400)
                                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                                
                                # Convertir en PhotoImage pour Tkinter
                                photo = ImageTk.PhotoImage(image)
                                
                                # Nettoyer l'ancienne image si elle existe
                                if hasattr(self.main_frame.wikipedia_label, 'image'):
                                    del self.main_frame.wikipedia_label.image
                                
                                # Garder une référence à la nouvelle image
                                self.main_frame.wikipedia_label.image = photo
                                
                                # Afficher l'image
                                self.main_frame.wikipedia_label.config(image=photo)
                                return True
                                
                            except Exception as e:
                                print(f"DEBUG: Erreur lors du traitement de l'image statique : {e}")
                                return False

                    except requests.exceptions.RequestException as e:
                        print(f"DEBUG: Erreur lors du téléchargement de l'image : {e}")
                        return False
                    except Exception as e:
                        print(f"DEBUG: Erreur lors du traitement de l'image : {e}")
                        return False

            print("DEBUG: Aucune image trouvée dans les pages")
            return False

        except requests.exceptions.RequestException as e:
            print(f"DEBUG: Erreur lors de la requête API : {e}")
            return False
        except Exception as e:
            print(f"DEBUG: Erreur inattendue : {e}")
            return False

    def _load_gif_animation(self, source, label):
        """Gère l'animation d'un GIF (depuis un fichier local ou un flux BytesIO)."""
        try:
            # Réinitialiser le label
            label.config(image="", text="")
            label.image = None

            # Ouvrir et redimensionner le GIF
            if isinstance(source, str):
                gif = Image.open(source)
            else:
                source.seek(0)
                gif = Image.open(source)

            # Obtenir les dimensions originales
            width, height = gif.size
            max_size = (400, 400)  # Revenir à la taille maximale de 400x400

            # Calculer le ratio pour le redimensionnement tout en préservant l'aspect
            ratio = min(max_size[0]/width, max_size[1]/height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            # Redimensionner le GIF
            resized_frames = []
            try:
                while True:
                    # Copier et redimensionner la frame
                    frame = gif.copy()
                    frame = frame.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized_frames.append(frame)
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass

            # Créer un nouveau GIF redimensionné
            output = io.BytesIO()
            resized_frames[0].save(
                output,
                format='GIF',
                save_all=True,
                append_images=resized_frames[1:],
                duration=gif.info.get('duration', 100),
                loop=0
            )
            output.seek(0)

            # Charger le GIF redimensionné
            if self.gif_animator.load_gif(output):
                self.gif_animator.play()

        except Exception as e:
            print(f"DEBUG: Erreur lors du chargement du GIF: {e}")
            label.config(text=f"Erreur lors du chargement du GIF: {e}")
            return False

    def reset_wikipedia_label(self):
        """Reset complet du label Wikipedia"""
        try:
            # Désactiver le bouton
            self.permanent_wiki_button.config(state=tk.DISABLED)

            # Supprimer toutes les références d'image
            self.wikipedia_photo = None
            
            # Arrêter l'animation GIF
            if self.gif_animator:
                self.gif_animator.stop()
            
            # Nettoyer le label
            label = self.main_frame.wikipedia_label
            label.config(image="", text="")
            label.image = None
            
            # Réinitialiser le dernier mot chargé
            self.last_loaded_word = None
            
            # Nettoyer la mémoire
            import gc
            gc.collect()

            # Forcer la mise à jour
            self.update_idletasks()
            
        except Exception as e:
            print(f"DEBUG: Erreur lors du reset du label: {e}")

    def create_local_image_dict(self):
        """Crée un dictionnaire d'images locales pour les termes anatomiques courants"""
        self.local_images = {
            "humérus": os.path.join("images", "humerus.jpg"),
            "scapula": os.path.join("images", "scapula.jpg"),
            "coeur": os.path.join("images", "coeur.jpg"),
            "poumon": os.path.join("images", "poumon.jpg"),
            # etc.
        }

    def show_local_image(self):
        """Affiche une image locale si disponible"""
        if not self.current_word:
            return False

        word_lower = self.current_word.lower()

        # Vérifier si nous avons un dictionnaire d'images locales
        if hasattr(self, 'local_images') and word_lower in self.local_images:
            img_path = resource_path(self.local_images[word_lower])
            if os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((400, 400), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.wikipedia_photo = photo
                    self.main_frame.wikipedia_label.config(image=photo, text="")
                    self.main_frame.wikipedia_label.image = photo
                    self.permanent_wiki_button.config(state=tk.NORMAL)
                    return True
                except Exception as e:
                    print(f"Erreur avec l'image locale: {e}")

        return False

    # -------------- Score / Stats / TTS / About --------------

    def update_score(self):
        self.bottom_frame.score_label.config(text=f"Score : {self.score} / {self.total_attempts}")

    def open_stats(self):
        stats_window = tk.Toplevel(self)
        stats_window.title("Statistiques")
        stats_window.geometry("400x300")  # Augmentation de la taille
        stats_window.minsize(400, 300)    # Taille minimale
        
        # Calcul des statistiques supplémentaires
        success_rate = (self.score / self.total_attempts * 100) if self.total_attempts > 0 else 0
        
        # Frame principal pour les stats
        main_frame = tk.Frame(stats_window, bg=self.bg_color_frame, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_label = tk.Label(
            main_frame,
            text="Statistiques de la session",
            font=("Arial", 16, "bold"),
            bg=self.bg_color_frame
        )
        title_label.pack(pady=(0, 20))
        
        # Statistiques détaillées
        stats_text = (
            f"Score actuel : {self.score} / {self.total_attempts}\n\n"
            f"Mots découverts correctement : {self.score}\n"
            f"Nombre total de tentatives : {self.total_attempts}\n"
            f"Taux de réussite : {success_rate:.1f}%\n\n"
            f"Mode actuel : {'Flashcard' if self.flashcard_mode else 'Normal'}\n"
            f"Chargement auto des images : {'Activé' if self.auto_load_images else 'Désactivé'}\n"
            f"Timer : {'Actif' if self.timer_active else 'Inactif'}"
        )
        
        stats_label = tk.Label(
            main_frame,
            text=stats_text,
            font=("Arial", 12),
            bg=self.bg_color_frame,
            justify=tk.LEFT
        )
        stats_label.pack(pady=10)
        
        # Bouton pour fermer
        close_button = tk.Button(
            main_frame,
            text="Fermer",
            font=("Arial", 12),
            bg=self.bg_color_buttons,
            command=stats_window.destroy
        )
        close_button.pack(pady=20)

    def text_to_speech(self):
        """Méthode désactivée car TTS n'est pas utilisé."""
        pass

    def show_about(self):
        messagebox.showinfo(
            "À propos d'AnatoLexic",
            "AnatoLexic - Logiciel d'apprentissage des termes d'anatomie/physiologie/pathologie.\n\n"
            "Version 1.2\n\n"
            "© 2024 Quentin LACHENAL\n"
            "Réalisé en tant qu'outil gratuit pour l'enseignement à l'Institut Supérieur de Rééducation Psychomotrice de Metz\n\n"
            "Projet final pour la validation du certificat CS50 HardvardX: https://pll.harvard.edu/course/cs50-introduction-computer-science\n"
            "Tous droits réservés."
        )

    def toggle_auto_images(self):
        """Bascule le chargement automatique des images."""
        self.auto_load_images = not self.auto_load_images
        self.bottom_frame.auto_images_button.config(
            text="Auto Images: ON" if self.auto_load_images else "Auto Images: OFF",
            bg=self.bg_color_frame if self.auto_load_images else self.bg_color_buttons
        )

    def toggle_auto_timer(self):
        """Bascule le timer automatique."""
        self.auto_timer = not self.auto_timer
        self.bottom_frame.auto_timer_button.config(
            text="Timer Auto: ON" if self.auto_timer else "Timer Auto: OFF",
            bg=self.bg_color_frame if self.auto_timer else self.bg_color_buttons
        )
        
        # Si on active le timer auto, démarrer le timer
        if self.auto_timer and not self.timer_active:
            self.toggle_timer()
        # Si on désactive le timer auto, arrêter le timer
        elif not self.auto_timer and self.timer_active:
            self.toggle_timer()