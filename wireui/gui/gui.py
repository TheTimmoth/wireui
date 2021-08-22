from tkinter import *

from .app import App

from ..library import strings


def run_gui():
  root = Tk()
  root.title(f"{strings.name} - {strings.version}")

  app = App(root)
  app.mainloop()
