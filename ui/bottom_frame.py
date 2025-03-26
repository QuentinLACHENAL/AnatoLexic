import tkinter as tk

class BottomFrame(tk.Frame):
    def __init__(self, parent, tts_available, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.tts_available = tts_available
        self.create_widgets()
        
    def create_widgets(self):
        # Score Label (left)
        self.score_label = tk.Label(
            self,
            text="Score : 0 / 0",
            font=("Arial", 12, "bold"),
            bg=self["bg"]
        )
        self.score_label.pack(side=tk.LEFT, padx=10)

        # Timer Label (center)
        self.timer_label = tk.Label(
            self,
            text="Temps restant : --",
            font=("Arial", 12),
            bg=self["bg"]
        )
        self.timer_label.pack(side=tk.LEFT, padx=10)

        # Message Label (center)
        self.message_label = tk.Label(
            self,
            text="",
            font=("Arial", 12),
            bg=self["bg"]
        )
        self.message_label.pack(side=tk.LEFT, padx=10)

        # Buttons Frame (right)
        buttons_frame = tk.Frame(self, bg=self["bg"])
        buttons_frame.pack(side=tk.RIGHT, padx=10)

        # Timer Button
        self.timer_button = tk.Button(
            buttons_frame,
            text="Démarrer Timer",
            font=("Arial", 10, "bold"),
            bg=self["bg"],
            command=self.parent.toggle_timer
        )
        self.timer_button.pack(side=tk.LEFT, padx=5)

        # Timer Auto Button
        self.auto_timer_button = tk.Button(
            buttons_frame,
            text="Timer Auto: OFF",
            font=("Arial", 10, "bold"),
            bg=self["bg"],
            command=self.parent.toggle_auto_timer
        )
        self.auto_timer_button.pack(side=tk.LEFT, padx=5)

        # Auto Images Button
        self.auto_images_button = tk.Button(
            buttons_frame,
            text="Auto Images: ON",
            font=("Arial", 10, "bold"),
            bg=self["bg"],
            command=self.parent.toggle_auto_images
        )
        self.auto_images_button.pack(side=tk.LEFT, padx=5)

        # Bouton Afficher image
        self.show_image_button = tk.Button(
            buttons_frame,
            text="Afficher image",
            font=("Arial", 10, "bold"),
            bg=self["bg"],
            command=self.parent.show_wikipedia_image
        )
        self.show_image_button.pack(side=tk.LEFT, padx=5)

        # TTS Button (if available)
        if self.tts_available:
            self.tts_button = tk.Button(
                buttons_frame,
                text="🔊",
                font=("Arial", 12),
                bg="lightyellow",
                command=self.parent.text_to_speech
            )
            self.tts_button.pack(side=tk.LEFT, padx=5)

        # Stats Button
        self.stats_button = tk.Button(
            buttons_frame,
            text="📊",
            font=("Arial", 12),
            bg="lightgray",
            command=self.parent.open_stats
        )
        self.stats_button.pack(side=tk.LEFT, padx=5)

        # About Button
        self.about_button = tk.Button(
            buttons_frame,
            text="ℹ️",
            font=("Arial", 12),
            bg="lightgray",
            command=self.parent.show_about
        )
        self.about_button.pack(side=tk.LEFT, padx=5)
