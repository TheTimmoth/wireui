#!/usr/bin/python3

# wireui
# A tool for creating and managing wireguard configs
# Version 0.2.0a
# (C) 2020-2021 Tim Schlottmann

from atexit import register
from tkinter import TclError

from .gui import run_gui
from .library import WireUI
from .ui import run_ui


def main():
  register(WireUI.get_instance("./settings.json").write_settings_to_file)
  register(WireUI.get_instance().write_sites_to_file)
  try:
    run_gui()
  except TclError:
    run_ui()


if __name__ == "__main__":
  main()
