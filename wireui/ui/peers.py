import ipaddress

from .console import print_error
from .console import print_message

from .shared import create_wireguard_config
from .shared import get_additional_allowed_ips
from .shared import get_endpoint
from .shared import get_new_peer_properties
from .shared import get_port
from .shared import get_persistent_keep_alive
from .shared import get_redirect_all_traffic
from .shared import yes_no_menu

from ..library import edit_connection_table
from ..library import ConnectionTable
from ..library import Peer
from ..library import PeerDoesExistError
from ..library import PeerDoesNotExistError
from ..library import WireUI


def list_peers(w: WireUI, site_name: str) -> int:
  peers = w.get_peer_names(site_name)
  if peers:
    print_message(0, "The following peers already exist:")
    for p in peers:
      print_message(0, p)
  else:
    print_message(0, "There are currently no peers.")
  return len(peers)


def add_peer(w: WireUI, site_name: str):
  peer_name = _get_peer_name(w, site_name, should_exist=False)
  allow_ipv4, allow_ipv6 = w.get_networks(site_name)
  try:
    w.add_peer(
      site_name,
      get_new_peer_properties(w, site_name, peer_name,
                              ConnectionTable([peer_name]), allow_ipv4,
                              allow_ipv6))
  except PeerDoesExistError:
    print_error(0, "Error: Peer does already exist. Do nothing...")
  else:
    edit_peer_connections(w, site_name)
    create_wireguard_config(w, site_name)


# TODO: add the new features --> transition this function to edit_peer
def rekey_peer(w: WireUI, site_name: str):
  peer_name = _get_peer_name(w, site_name, should_exist=True)
  try:
    w.rekey_peer(site_name, peer_name)
  except PeerDoesNotExistError:
    print_error(0, "Error: Peer does not exist. Do nothing...")
  else:
    create_wireguard_config(w, site_name)


def delete_peer(w: WireUI, site_name: str):
  peer_name = _get_peer_name(w, site_name, should_exist=True)
  if yes_no_menu(f"Do you really want to delete peer {peer_name}?"):
    try:
      w.delete_peer(site_name, peer_name)
    except PeerDoesNotExistError:
      print_error(0, "Error: Peer does not exist. Do nothing...")

  edit_peer_connections(w, site_name)
  create_wireguard_config(w, site_name)


def edit_peer_connections(w: WireUI, site_name: str):
  """ Edit the peer connection matrix """

  # Create an empty connection table
  peer_names = w.get_peer_names(site_name)
  ct = ConnectionTable(peer_names)

  # Populate table with actual data
  for i in range(len(peer_names)):
    peer = w.get_peer(site_name, ct.row_names[i])
    for j in range(len(peer_names)):
      if ct.column_names[j] in peer.outgoing_connected_peers:
        ct.setitem(i, j, 1)
    ct.setitem(i, len(peer_names), peer.main_peer)

  # Edit table
  input("Please edit the connection table. Press ENTER to continue...")
  ct = edit_connection_table(ct)

  # Update peers with changed connection table
  for p in peer_names:
    peer_old = w.get_peer(site_name, p)

    # If a peer now has ingoing connections, ask for endpoint and port
    if not peer_old.ingoing_connected_peers and ct.get_ingoing_connected_peers(
        p):
      print_message(0, f"Collecting properties of peer {p} (ingoing)...")
      if peer_old.endpoint == "":
        endpoint = get_endpoint()
      else:
        endpoint = peer_old.endpoint
      if peer_old.port == 0:
        port = get_port()
      else:
        port = peer_old.port
      if peer_old.additional_allowed_ips == []:
        allow_ipv4, allow_ipv6 = w.get_networks(site_name)
        additional_allowed_ips = get_additional_allowed_ips(
          allow_ipv4, allow_ipv6)
      else:
        additional_allowed_ips = []
    else:
      endpoint = peer_old.endpoint
      port = peer_old.port
      additional_allowed_ips = peer_old.additional_allowed_ips

    # If a peer now has outgoing connections, ask for persistent_keep_alive and redirect_all_traffic
    if peer_old.persistent_keep_alive == -1:
      persistent_keep_alive = get_persistent_keep_alive()
    else:
      persistent_keep_alive = peer_old.persistent_keep_alive
    if not peer_old.outgoing_connected_peers and ct.get_outgoing_connected_peers(
        p):
      print_message(0, f"Collecting properties of peer {p} (outgoing)...")
      if peer_old.redirect_all_traffic == None:
        redirect_all_traffic = get_redirect_all_traffic()
      else:
        redirect_all_traffic = peer_old.redirect_all_traffic
    else:
      persistent_keep_alive = peer_old.persistent_keep_alive
      redirect_all_traffic = peer_old.redirect_all_traffic

    w.set_peer(
      site_name,
      Peer(
        peer_old.name,
        additional_allowed_ips,
        ct.get_outgoing_connected_peers(p),
        ct.get_main_peer(p),
        ct.get_ingoing_connected_peers(p),
        endpoint,
        port,
        persistent_keep_alive,
        redirect_all_traffic,
        peer_old.post_up,
        peer_old.post_down,
        peer_old.ipv6_routing_fix,
      ))

  create_wireguard_config(w, site_name)


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
