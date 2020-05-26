from atexit import register

from .console import set_verbosity

from .menus import start_message
from .menus import entrypoint_menu

from ..library import WireUI
from ..library import SettingDoesNotExistError

_SETTINGS_PATH = "./settings.json"


def run_ui():
  w = WireUI("./settings.json")
  register(w.write_settings_to_file)
  register(w.write_sites_to_file)
  set_verbosity(w.get_setting("verbosity"))
  start_message()
  entrypoint_menu(w)
