import tkinter as tk

class AdvancedFrame(tk.Frame):
    def __init__(self, parent, flashcard_mode, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.flashcard_mode = flashcard_mode
        self.create_widgets()

    def create_widgets(self):
        self.flashcard_button = tk.Button(
            self,
            text="Désactiver Mode Flashcard (ON)" if self.flashcard_mode else "Activer Mode Flashcard (OFF)",
            font=("Arial", 12, "bold"),
            bg=self.master.bg_color_buttons,
            command=self.master.toggle_flashcard_mode
        )
        self.flashcard_button.pack(side=tk.LEFT, padx=5)

        self.suggest_letter_button = tk.Button(
            self,
            text="Proposer une lettre",
            font=("Arial", 12, "bold"),
            bg=self.master.bg_color_buttons,
            command=self.master.suggest_letter
        )
        self.suggest_letter_button.pack(side=tk.LEFT, padx=5)


