from atexit import register

from .console import set_verbosity
from .console import print_error
from .console import print_header

from .menus import entrypoint_menu

from .results import get_result_list_messages

from ..library import WireUI


def run_ui():
  w = WireUI.get_instance()
  isr = w.get_startup_result()

  print_header("Import Results")
  s = ""
  for site in isr.get_sites():
    srl = isr.get_site_results(site)

    s += f"Site {site}:\n"
    s += get_result_list_messages(srl)

    for peer in isr.get_peer_results(site).get_peers():
      prl = isr.get_peer_results(site).get_peer_results(peer)

      s += f"Peer {peer}:\n"
      s += get_result_list_messages(prl)

  print_error(0, s)

  register(WireUI.get_instance("./settings.json").write_settings_to_file)
  register(WireUI.get_instance().write_sites_to_file)
  set_verbosity(w.get_setting("verbosity"))
  entrypoint_menu(w)
