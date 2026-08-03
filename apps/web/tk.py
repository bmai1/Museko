import tkinter as tk
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
from essentia_model.genre_discogs400 import classify

class Museko:
    def __init__(self, root):
        self.root = root

        root.title("Museko")
        root.geometry("500x500")

        self.upload_button = tk.Button(root, text="Upload mp3", command=self.upload)
        self.upload_button.pack(pady=(25,0))

        self.genre_prediction = tk.Label(root)
        self.genre_prediction.pack()

    def upload(self):
        filepath = askopenfilename()

        buffer = classify(filepath) # buffer of matplotlib figure for genre predictions
        image = Image.open(buffer)
        image = image.resize((400, 400), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(image)
        self.genre_prediction.config(image=tk_image)
        self.genre_prediction.image = tk_image

root = tk.Tk()
app = Museko(root)
root.mainloop()

# Tkinter window for testing on macOS without running Flask