#!/usr/bin/python3

# wireui
# A tool for creating and managing wireguard configs
# Version 0.1.0a
# (C) 2020 Tim Schlottmann

# import ui.menus
# import inputOutput.console as console
# from database.settings import settings

from atexit import register

from .library import WireUI

from .ui import run_ui


def main():
  register(WireUI.get_instance("./settings.json").write_settings_to_file)
  register(WireUI.get_instance().write_sites_to_file)
  run_ui()


if __name__ == "__main__":
  main()
