import tkinter as tk
from tkinter import ttk

from PIL import ImageTk, Image


class Canvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)

    def _bound_to_mousewheel(self, event):
        self.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.yview_scroll(int(-1 * (event.delta / 120)), "units")


class Button(ttk.Button):
    def __init__(self, text, command, parent, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)


class Label(ttk.Label):
    wraplength = 450

    def __init__(self, parent, text, justify=tk.CENTER, **kwargs):
        super().__init__(parent, text=text, justify=justify, wraplength=self.wraplength, **kwargs)


class NotebookPage(ttk.Frame):
    def __init__(self, parent):
        kwargs = {
            "width": parent.cget("width"),
            "height": parent.cget("height")
        }
        super().__init__(parent, **kwargs)


class ImageButton(tk.Button):
    def __init__(self, parent, command, image="placeholder.png", dimensions=(20, 20), **kwargs):
        self.dimensions = dimensions
        img = Image.open(image)
        photo = ImageTk.PhotoImage(img.resize(dimensions))
        self.image = photo
        super().__init__(parent, command=command, image=photo, **kwargs)

    def setImage(self, image, dimensions=None):
        if dimensions is None:
            dimensions = self.dimensions
        img = Image.open(image)
        photo = ImageTk.PhotoImage(img.resize(dimensions))
        self.configure(image=photo)
        self.image = photo


class RuneSlotImage(ImageButton):
    def __init__(self, parent, command, image="placeholder.png", dimensions=(150, 200), **kwargs):
        super().__init__(parent, command, image, dimensions, **kwargs)


def onFrameConfigure(canvas):  # Update canvas to match frame
    canvas.configure(scrollregion=canvas.bbox("all"))


def createGameWindow():
    w = tk.Tk()
    w.title("Adventure Game")
    # w.geometry("700x450+500+100")
    w.resizable(False, False)
    w.grid_columnconfigure(0, weight=1)
    w.grid_rowconfigure(0, weight=1)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TButton", font=(None, 15))
    style.map('TButton', background=[('active', 'gray70')])
    style.configure("TLabel", font=(None, 15))

    return w


def createGameNotebook(frame):
    notebook = ttk.Notebook(frame)
    # notebook.configure(width=690, height=420)
    notebook.grid()
    return notebook


def createNotebookPage(notebook, name):
    page = NotebookPage(notebook)
    notebook.add(page, text=name)
    page.grid_columnconfigure(0, weight=1)
    return page


def clear(frame):
    for i in frame.winfo_children():
        i.destroy()
