import tkinter as tk
from tkinter import filedialog

def select_file():
    # Create a Tkinter root window (it won't be shown)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open the file dialog and let the user select a file
    file_path = filedialog.askopenfilename(
        title="Escoge Archivo (.edgerc):",
        filetypes=(("All files", "*.*"), ("Config files", "*.edgerc"))
    )

    # Return the selected file path
    return file_path

# Usage
file_location = select_file()
print(f"Selected file: {file_location}")