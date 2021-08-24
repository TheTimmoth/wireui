import ipaddress

from .console import leave_menu
from .console import print_error
from .console import print_list
from .console import print_message
from .console import write_header
from .console import yes_no_menu

from .shared import create_wireguard_config
from .shared import edit_connection_table
from .shared import edit_peer_connections
from .shared import get_additional_allowed_ips
from .shared import get_endpoint
from .shared import get_new_peer_properties
from .shared import get_port
from .shared import get_persistent_keep_alive
from .shared import get_redirect_all_traffic

from ..library import ConnectionTable
from ..library import Peer
from ..library import PeerDoesExistError
from ..library import PeerDoesNotExistError
from ..library import WireUI


def add_peer(w: WireUI, site_name: str):
  write_header("Create new peer")

  peer_name = __get_peer_name(w, site_name, should_exist=False)
  allow_ipv4, allow_ipv6, _ = w.get_networks(site_name)
  dns = w.get_dns(site_name)
  try:
    w.add_peer(
      site_name,
      get_new_peer_properties(w, site_name, peer_name, dns,
                              ConnectionTable([peer_name]), allow_ipv4,
                              allow_ipv6))
  except PeerDoesExistError:
    print_error(0, "Error: Peer does already exist. Do nothing...")
  else:
    edit_peer_connections(w, site_name)
    create_wireguard_config(w, site_name)

  leave_menu()


# TODO: add the new features --> transition this function to edit_peer
def rekey_peer(w: WireUI, site_name: str):
  write_header("Rekey a peer")
  peer_name = __get_peer_name(w, site_name, should_exist=True)
  try:
    w.rekey_peer(site_name, peer_name)
  except PeerDoesNotExistError:
    print_error(0, "Error: Peer does not exist. Do nothing...")
  else:
    create_wireguard_config(w, site_name)
  leave_menu()


def delete_peer(w: WireUI, site_name: str):
  write_header("Delete a peer")
  peer_name = __get_peer_name(w, site_name, should_exist=True)
  if yes_no_menu(f"Do you really want to delete peer {peer_name}?"):
    try:
      w.delete_peer(site_name, peer_name)
    except PeerDoesNotExistError:
      print_error(0, "Error: Peer does not exist. Do nothing...")

  edit_peer_connections(w, site_name)
  create_wireguard_config(w, site_name)
  leave_menu()


def __get_peer_name(w: WireUI, site_name: str, should_exist: bool) -> str:
  while True:
    write_header("Get peer name")
    __list_peers(w, site_name)
    peer_name = input("Please enter the name of the peer: ")
    exist = w.peer_exists(site_name, peer_name)
    if (should_exist and exist) or (not should_exist and not exist):
      leave_menu()
      return peer_name
    elif should_exist and not exist:
      print_error(0, f"Error: {peer_name} does not exist.")
    elif not should_exist and exist:
      print_error(0, f"Error: {peer_name} does already exist.")
    leave_menu()


def __list_peers(w: WireUI, site_name: str) -> int:
  peers = w.get_peer_names(site_name)
  if peers:
    print_message(0, "The following peers already exist:")
    print_list(peers)
  else:
    print_message(0, "There are currently no peers.")
