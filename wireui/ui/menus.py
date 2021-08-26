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

from ..library import strings
from ..library import WireUI


def entrypoint_menu(w: WireUI):
  while True:
    print_header("Main menu")

    options = {
      "1": "Create new site",
    }
    if len(w.get_sites()):
      options.update({
        "2": "Edit properties of existing site",
        "3": "Delete existing site",
        "4": "Edit connection table",
        "5": "Go to the site menu",
        "6": "Recreate config files",
        "a": "Informations about this program",
        "q": "Exit",
      })
      default = "6"
    else:
      default = "1"

    choice = options_menu(options=options, default=default)

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
    print_header(f"Site \"{site_name}\"")
    peers_count = len(w.get_peer_names(site_name))

    # TODO: Remove this hint when editing is possible
    print_message(0,
                  "For full editing of peers please use the sites.json file!")

    options = {
      "1": "Add peer",
    }
    default = "1"
    if len(w.get_peer_names(site_name)):
      options.update({
        "2": "Edit properties of a peer",
        "3": "Delete peer",
        "4": "Create new keys for a peer",
        "b": "Back",
        "q": "Exit",
      })
      default = "b"

    choice = options_menu(options=options, default=default)

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
  print_header("About")
  print_message(0, strings.name)
  print_message(0, strings.description)
  print_message(0, f"Version {strings.version}")
  print_message(0, f"{strings.copyright} {strings.author}")
  print_message(0, "")
  input("Press ENTER to go back...")
  leave_menu()


def __exit(i):
  clear_screen()
  print_message(0, "Bye")
  exit(i)
