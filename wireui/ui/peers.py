from typing import Optional
from .console import leave_menu
from .console import print_error
from .console import print_list
from .console import print_message
from .console import print_header
from .console import yes_no_menu

from .shared import change_existing_peer_properties
from .shared import create_wireguard_config
from .shared import edit_peer_connections
from .shared import get_new_peer_properties
from .shared import get_populated_connection_table

from ..library import ConnectionTable
from ..library import PeerDoesNotExistError
from ..library import WireUI

from ..shared import strings


def add_peer(w: WireUI, site_name: str, peer_name: Optional[str] = None):
  print_header(f"{strings['peer_actions']['add_peer_header']}")

  if not peer_name:
    peer_name = __get_peer_name(w, site_name, should_exist=False)

  allow_ipv4, allow_ipv6, _ = w.get_networks(site_name)
  dns = w.get_dns(site_name)

  w.add_peer(
    site_name,
    get_new_peer_properties(w, site_name, peer_name, dns,
                            ConnectionTable([peer_name]), allow_ipv4,
                            allow_ipv6))

  edit_peer_connections(w, site_name)
  create_wireguard_config(w, site_name)

  leave_menu()


def edit_peer(site_name: str):
  print_header(f"{strings['peer_actions']['edit_peer_header']}")

  w = WireUI.get_instance()

  peer_name = __get_peer_name(w, site_name, should_exist=True)
  allow_ipv4, allow_ipv6, _ = w.get_networks(site_name)
  dns = w.get_dns(site_name)

  w.set_peer(
    site_name,
    change_existing_peer_properties(
      w, site_name, peer_name, dns,
      get_populated_connection_table(site_name=site_name), allow_ipv4,
      allow_ipv6))

  create_wireguard_config(w, site_name)

  print_header()
  if yes_no_menu(f"{strings['peer_actions']['edit_peer_another_yes_no']}",
                 False):
    edit_peer(site_name)

  leave_menu()


def rekey_peer(w: WireUI, site_name: str):
  print_header(f"{strings['peer_actions']['rekey_peer_header']}")
  peer_name = __get_peer_name(w, site_name, should_exist=True)
  w.rekey_peer(site_name, peer_name)
  create_wireguard_config(w, site_name)
  leave_menu()


def delete_peer(w: WireUI, site_name: str):
  print_header(f"{strings['peer_actions']['delete_peer_header']}")
  peer_name = __get_peer_name(w, site_name, should_exist=True)
  if yes_no_menu(
      f"{strings['peer_actions']['delete_peer_yes_no']}".format(peer_name)):
    w.delete_peer(site_name, peer_name)
  edit_peer_connections(w, site_name)
  create_wireguard_config(w, site_name)
  leave_menu()


def __get_peer_name(w: WireUI, site_name: str, should_exist: bool) -> str:
  while True:
    print_header(f"{strings['peer_actions']['peer_name_header']}")
    __list_peers(w, site_name)
    peer_name = input(f"{strings['peer_actions']['peer_name_enter']}")
    exist = w.peer_exists(site_name, peer_name)
    if (should_exist and exist) or (not should_exist and not exist):
      leave_menu()
      return peer_name
    elif should_exist and not exist:
      print_error(
        0, f"{strings['peer_actions']['peer_name_not_exists_error']}".format(
          peer_name))
    elif not should_exist and exist:
      print_error(
        0, f"{strings['peer_actions']['peer_name_exists_error']}".format(
          peer_name))
    leave_menu()


def __list_peers(w: WireUI, site_name: str) -> int:
  peers = w.get_peer_names(site_name)
  if peers:
    print_message(0, f"{strings['peer_actions']['list_peers']}")
    print_list(peers)
  else:
    print_message(0, f"{strings['peer_actions']['list_peers_empty']}")
