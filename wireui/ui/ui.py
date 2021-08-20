from atexit import register

from .console import set_verbosity

from .menus import entrypoint_menu

from .shared import print_error

from ..library import DataIntegrityError
from ..library import WireUI
from ..library import WireguardNotFoundError


def run_ui():
  s = ""
  try:
    w = WireUI("./settings.json")
  except DataIntegrityError as e:
    s += f"{e}\n"
  except WireguardNotFoundError as e:
    s += f"{e}\n"
  if s:
    print_error(0, s[:-1])
    return

  register(w.write_settings_to_file)
  register(w.write_sites_to_file)
  set_verbosity(w.get_setting("verbosity"))
  entrypoint_menu(w)
