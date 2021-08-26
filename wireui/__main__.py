#!/usr/bin/python3

# wireui
# A tool for creating and managing wireguard configs
# Version 0.1.0b
# (C) 2020-2021 Tim Schlottmann

# import ui.menus
# import inputOutput.console as console
# from database.settings import settings

from .library import WireUI

from .ui import run_ui


def main():
  w = WireUI.get_instance(".\settings.json")

  run_ui()


if __name__ == "__main__":
  main()
