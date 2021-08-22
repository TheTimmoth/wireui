from .console import set_verbosity
from .menus import entrypoint_menu

from ..library import WireUI


def run_ui():
  w = WireUI.get_instance()
  set_verbosity(w.get_setting("verbosity"))
  entrypoint_menu(w)
