import tkinter as tk
import traceback
import os

if __name__ == "__main__":
    try:
        from app import Application
        app = Application()
        app.mainloop()
    except Exception as e: 
        error_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_log.txt")
        with open(error_path, "w") as f:
            f.write(f"Erreur: {str(e)}\n")
            f.write(traceback.format_exc())
        print(f"Une erreur s'est produite: {e}")
        input("Appuyez sur Entrée pour fermer...")  # Empêche la fenêtre de se fermer immédiatement