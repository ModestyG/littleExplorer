import tkinter as tk
from tkinter import ttk


class Button(ttk.Button):
    def __init__(self, text, command, parent):
        kwargs = {
            "text": text,
            "command": command
        }
        super().__init__(parent, **kwargs)


class Label(ttk.Label):
    wraplength = 450

    def __init__(self, parent, text, justify=tk.CENTER):
        kwargs = {
            "text": text,
            "justify": justify,
            "wraplength": self.wraplength,
        }
        super().__init__(parent, **kwargs)


class NotebookPage(ttk.Frame):
    def __init__(self, parent):
        kwargs = {
            "width": parent.cget("width"),
            "height": parent.cget("height")
        }
        super().__init__(parent, **kwargs)


def createGameWindow():
    w = tk.Tk()
    w.title("Adventure Game")
    #w.geometry("500x500+500+100")
    w.resizable(False, False)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TButton", font=(None, 15))
    style.map('TButton', background=[('active', 'gray70')])
    style.configure("TLabel", font=(None, 15))
    style.configure("Walkable.TButton", background="red", font=(None, 9))
    style.map('Walkable.TButton', background=[('active', 'red4')])
    style.configure("Player.TButton", background="blue", font=(None, 9))
    style.map('Player.TButton', background=[('active', 'blue4')])
    style.configure("Enemy.TButton", background="green", font=(None, 9))
    style.map('Enemy.TButton', background=[('active', 'green4')])
    style.configure("Free.TButton", font=(None, 9))
    style.map('Free.TButton', background=[('active', 'gray70')])


    return w


def createGameNotebook(frame):
    notebook = ttk.Notebook(frame)
    notebook.grid()
    return notebook


def createNotebookPage(notebook, name):
    page = NotebookPage(notebook)
    notebook.add(page, text=name)
    return page


def clear(frame):
    for i in frame.winfo_children():
        i.destroy()
