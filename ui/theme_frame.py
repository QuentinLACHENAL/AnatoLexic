import tkinter as tk

class ThemeFrame(tk.Frame):
    def __init__(self, parent, theme_var, sous_theme_var, update_sous_themes, themes, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.theme_var = theme_var
        self.sous_theme_var = sous_theme_var
        self.update_sous_themes = update_sous_themes
        self.themes = themes
        
        self._create_widgets()
        
    def _create_widgets(self):
        theme_label = tk.Label(
            self,
            text="Thème :",
            font=("Arial", 14, "bold"),
            fg=self.master.fg_color_text,
            bg=self.master.bg_color_frame
        )
        theme_label.pack(side=tk.LEFT, padx=5)

        theme_menu = tk.OptionMenu(
            self,
            self.theme_var,
            *self.themes,
            command=self.update_sous_themes
        )
        theme_menu.config(
            font=("Arial", 12),
            fg=self.master.fg_color_text,
            width=20,
            bg=self.master.bg_color_buttons
        )
        theme_menu.pack(side=tk.LEFT, padx=5)

        sous_theme_label = tk.Label(
            self,
            text="Sous-thème :",
            font=("Arial", 14, "bold"),
            fg=self.master.fg_color_text,
            bg=self.master.bg_color_frame
        )
        sous_theme_label.pack(side=tk.LEFT, padx=10)

        self.sous_theme_menu = tk.OptionMenu(self, self.sous_theme_var, "")
        self.sous_theme_menu.config(
            font=("Arial", 12),
            fg=self.master.fg_color_text,
            width=20,
            bg=self.master.bg_color_buttons
        )
        self.sous_theme_menu.pack(side=tk.LEFT, padx=5)
