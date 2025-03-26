import os
import sys

def resource_path(relative_path):
    """
    Returns absolute path to resource, compatible with PyInstaller (--onefile mode).
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller creates a temp folder and stores path in _MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")  # Changé de ".." à "."

    return os.path.join(base_path, relative_path)
