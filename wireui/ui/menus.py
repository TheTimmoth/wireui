from .console import clear_screen
from .console import leave_menu
from .console import options_menu
from .console import print_error
from .console import print_message
from .console import print_header

from .peers import add_peer, edit_peer
from .peers import delete_peer
from .peers import rekey_peer

from .shared import create_wireguard_config
from .shared import edit_peer_connections

from .sites import add_site
from .sites import edit_site
from .sites import delete_site
from .sites import get_site_name

from ..library import WireUI
from ..shared import strings


def entrypoint_menu(w: WireUI):
  while True:
    print_header(f"{strings['entrypoint_menu']['header']}")

    options = {
      "1": f"{strings['entrypoint_menu']['add']}",
      "a": f"{strings['entrypoint_menu']['about']}",
      "q": f"{strings['misc']['exit']}",
    }
    default = "1"
    order = ["1", "a", "q"]
    if len(w.get_sites()):
      options.update({
        "2": f"{strings['entrypoint_menu']['edit']}",
        "3": f"{strings['entrypoint_menu']['delete']}",
        "4": f"{strings['entrypoint_menu']['edit_connections']}",
        "5": f"{strings['entrypoint_menu']['site_menu']}",
        "6": f"{strings['entrypoint_menu']['config_files']}",
      })
      default = "6"
      order = ["1", "2", "3", "4", "5", "6", "a", "q"]

    choice = options_menu(options=options, default=default, order=order)

    if choice == "1":
      leave_menu()
      site_menu(w, add_site(w))
    elif choice == "2":
      leave_menu()
      site_menu(w, edit_site())
    elif choice == "3":
      leave_menu()
      delete_site(w)
    elif choice == "4":
      leave_menu()
      edit_peer_connections(w, get_site_name(w, should_exist=True))
    elif choice == "5":
      site_menu(w, get_site_name(w, True))
    elif choice == "6":
      create_wireguard_config(w, get_site_name(w, should_exist=True))
      leave_menu()
    elif choice == "a":
      leave_menu()
      __about()
    elif choice == "q":
      __exit(0)

    print_message(0, "")


def site_menu(w: WireUI, site_name: str):
  leave = False
  while not leave:
    print_header(f"{strings['site_menu']['header']}".format(site_name))
    peers_count = len(w.get_peer_names(site_name))

    options = {
      "1": f"{strings['site_menu']['add']}",
      "b": f"{strings['misc']['back']}",
      "q": f"{strings['misc']['exit']}",
    }
    order = ["1", "b", "q"]
    default = "1"
    if len(w.get_peer_names(site_name)):
      options.update({
        "2": f"{strings['site_menu']['edit']}",
        "3": f"{strings['site_menu']['delete']}",
        "4": f"{strings['site_menu']['rekey']}",
      })
      order = ["1", "2", "3", "4", "b", "q"]
      default = "b"

    choice = options_menu(options=options, default=default, order=order)

    if choice == "1":
      add_peer(w, site_name)
    elif choice == "2":
      edit_peer(site_name)
    elif choice == "3":
      delete_peer(w, site_name)
    elif choice == "4":
      rekey_peer(w, site_name)
    elif choice == "b":
      leave = True
      leave_menu()
    elif choice == "q":
      __exit(0)

    print_message(0, "")


def __about():
  print_header(f"{strings['misc']['about']}")
  print_message(0, f"{strings['app_information']['name']}")
  print_message(0, f"{strings['app_information']['description']}")
  print_message(
    0, f"{strings['misc']['version']} {strings['app_information']['version']}")
  print_message(
    0,
    f"{strings['app_information']['copyright']} {strings['app_information']['author']}"
  )
  print_message(0, "")
  input(f"{strings['misc']['enter_back']}")
  leave_menu()


def __exit(i):
  clear_screen()
  print_message(0, f"{strings['misc']['bye']}")
  exit(i)
