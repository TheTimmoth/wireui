import ipaddress

from .console import print_error, print_message

from ..library import ConnectionTable
from ..library import Peer
from ..library import WireUI

def yes_no_menu(string) -> bool:
  valid = False
  while not valid:
    choice = input(string + " [y/n] ")
    if choice == "y":
      choice = True
      valid = True
    elif choice == "n":
      choice = False
      valid = True
  return choice

def create_wireguard_config(w: WireUI, site_name: str):
  created_files = w.create_wireguard_config(site_name)
  print_message(1, "The following files have been created:")
  for f in created_files:
    print_message(1, f)
  print_message(0, f"{len(created_files)} file(s) have been created.")


def get_new_peer_properties(peer_name: str, ct: ConnectionTable) -> Peer:
  print_message(0, f"Collecting properties of peer {peer_name}...")

  # If peer has ingoing connections endpoint and port is needed
  if ct.get_ingoing_connected_peers(peer_name):
    endpoint = get_endpoint()
    port = get_port()

    additional_allowed_ips = get_additional_allowed_ips()
  else:
    endpoint = ""
    port = 0
    additional_allowed_ips = []

  # If peer has outgoing connections redirect_all_traffic is needed
  if ct.get_outgoing_connected_peers(peer_name):
    redirect_all_traffic = get_redirect_all_traffic()
  else:
    redirect_all_traffic = None

  return Peer(peer_name, additional_allowed_ips, ct.get_outgoing_connected_peers(peer_name), ct.get_ingoing_connected_peers(peer_name), endpoint, port, redirect_all_traffic)


# TODO: is correct messages
def get_endpoint() -> str:
  return input("Please enter the URL or IP address of the server: ")


# TODO: is correct messages
def get_port() -> int:
  while True:
    port = input("Please enter the port the adapter should listen on: ")
    try:
      port = int(port)
    except ValueError:
      print_error(0, "Error: The port was not a valid integer.")
      continue
    else:
      if port <= 0 or port > 65535:
        print_error(0, "Error: The port should be between 0 and 65535")
        continue
    return port


# TODO: is correct messages
def get_additional_allowed_ips() -> list:
  l = []
  if yes_no_menu("Do you want to add an additional AllowedIP network?"):
    while True:
      try:
        l.append(str(ipaddress.ip_network(input("Please enter an additional ip network to add to the AllowedIPs List: ")).with_prefixlen))
      except ValueError as e:
        print_error(0, "Error: Input is not a valid IP network.")
        print_error(2, e)
      else:
        if yes_no_menu("Do you want to add another network?"):
          continue
        else:
          break

  return l


# TODO: is correct messages
def get_redirect_all_traffic() -> bool:
  return yes_no_menu("Please enter if all traffic from the peer should be redirected:")
