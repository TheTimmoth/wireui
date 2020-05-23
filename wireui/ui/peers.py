from .console import print_error
from .console import print_message

from ..library import PeerDoesExistError
from ..library import PeerDoesNotExistError
from ..library import WireUI


def list_peers(w: WireUI, site_name: str) -> int:
  peers = w.get_peers(site_name)
  if peers:
    print_message(0, "The following peers already exist:")
    for p in peers:
      print_message(0, p)
  else:
    print_message(0, "There are currently no peers.")
  return len(peers)


def add_peer(w: WireUI, site_name: str):
  peer_name = _get_peer_name(w, site_name, should_exist=False)
  try:
    w.add_peer(site_name, peer_name)
  except PeerDoesExistError as e:
    print_error(0, "Error: Peer does already exist. Do nothing...")
  else:
    w.create_wireguard_config(site_name)


def rekey_peer(w: WireUI, site_name: str):
  peer_name = _get_peer_name(w, site_name, should_exist=True)
  try:
    w.rekey_peer(site_name, peer_name)
  except PeerDoesNotExistError as e:
    print_error(0, "Error: Peer does not exist. Do nothing...")
  else:
    w.create_wireguard_config(site_name)


def delete_peer(w: WireUI, site_name: str):
  peer_name = _get_peer_name(w, site_name, should_exist=True)
  try:
    w.delete_peer(site_name, peer_name)
  except PeerDoesNotExistError:
    print_error(0, "Error: Peer does not exist. Do nothing...")
  else:
    w.create_wireguard_config(site_name)


def _get_peer_name(w: WireUI, site_name: str, should_exist: bool) -> str:
  while True:
    peer_name = input("Please enter the name of the peer: ")
    exist = w.peer_exists(site_name, peer_name)
    if (should_exist and exist) or (not should_exist and not exist):
      return peer_name
    elif should_exist and not exist:
      print_error(0, f"Error: {peer_name} does not exist.")
    elif not should_exist and exist:
      print_error(0, f"Error: {peer_name} does already exist.")
