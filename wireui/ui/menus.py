from .console import clear_screen
from .console import leave_menu
from .console import print_error
from .console import print_message
from .console import write_header

from .peers import add_peer
from .peers import delete_peer
from .peers import edit_peer_connections
from .peers import rekey_peer

from .shared import create_wireguard_config

from .sites import add_site
from .sites import delete_site
from .sites import get_site_name

from ..library import strings
from ..library import WireUI


def entrypoint_menu(w: WireUI):
  while True:
    write_header("Main menu")

    sites_count = len(w.get_sites())
    print_message(0, "1: Create new site")
    if sites_count:
      print_message(0, "2: Edit existing site")
      print_message(0, "3: Delete existing site")
      print_message(0, "4: Recreate config files")
    print_message(0, "a: Informations about this program")
    print_message(0, "q: Exit")
    choice = input("What do you want to do? ")

    if choice == "1":
      leave_menu()
      site_menu(w, add_site(w))
    elif choice == "2" and sites_count:
      leave_menu()
      site_menu(w, get_site_name(w, should_exist=True))
    elif choice == "3" and sites_count:
      leave_menu()
      delete_site(w)
    elif choice == "4" and sites_count:
      leave_menu()
      create_wireguard_config(w, get_site_name(w, should_exist=True))
    elif choice == "a":
      leave_menu()
      __about()
    elif choice == "q":
      __exit(0)

    print_message(0, "")


def site_menu(w: WireUI, site_name: str):
  leave = False
  while not leave:
    write_header(f"Site \"{site_name}\"")
    peers_count = len(w.get_peer_names(site_name))

    # TODO: Remove this hint when editing is possible
    print_message(0,
                  "For full editing of peers please use the sites.json file!")

    print_message(0, "1: Add peer")
    if peers_count:
      print_message(0, "2: Create new keys for a peer")
      print_message(0, "3: Delete peer")
      print_message(0, "4: Edit connection table")
    print_message(0, "b: Back")
    print_message(0, "q: Exit")
    choice = input("What do you want to do? ")

    if choice == "1":
      add_peer(w, site_name)
    elif choice == "2" and peers_count:
      rekey_peer(w, site_name)
    elif choice == "3" and peers_count:
      delete_peer(w, site_name)
    elif choice == "4" and peers_count:
      edit_peer_connections(w, site_name)
    elif choice == "b":
      leave = True
      leave_menu()
    elif choice == "q":
      __exit(0)

    print_message(0, "")


def __about():
  write_header("About")
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
