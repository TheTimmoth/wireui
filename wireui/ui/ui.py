from atexit import register

from .console import set_verbosity
from .console import print_error
from .console import print_header

from .menus import entrypoint_menu

from .results import get_result_list_messages

from ..library import WireUI


def run_ui():
  w = WireUI.get_instance()

  if not w.startup_result.get_success():
    print_header("Import Results")
    s = ""
    for site in w.startup_result:
      data_integrity_message = w.startup_result[site]

      if not data_integrity_message.get_success():
        s += f"Site {site}:\n"
        s += get_result_list_messages(data_integrity_message.site_result,
                                      "|- ")

        for rl in data_integrity_message.peer_results:
          if not rl.get_success():
            s += f"|- Peer {rl.name}:\n"
            s += get_result_list_messages(rl, "   |- ")
    s = s[:-1]
    print_error(0, s)
    input("Press ENTER to exit...")

  else:
    register(WireUI.get_instance("./settings.json").write_settings_to_file)
    register(WireUI.get_instance().write_sites_to_file)
    set_verbosity(w.get_setting("verbosity"))
    entrypoint_menu(w)
