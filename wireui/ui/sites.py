import ipaddress

from .console import print_message
from .console import print_error

from .shared import create_wireguard_config
from .shared import get_new_peer_properties
from .shared import yes_no_menu

from ..library import edit_connection_table
from ..library import edit_string
from ..library import ConnectionTable
from ..library import Peer
from ..library import Site
from ..library import SiteDoesExistError
from ..library import SiteDoesNotExistError
from ..library import WireUI


def list_sites(w: WireUI) -> int:
  sites = w.get_sites()
  if sites:
    print_message(0, "The following sites do exist:")
    for s in sites:
      print_message(0, s)
  else:
    print_message(0, "There are currently no sites.")
  return len(sites)


def add_site(w: WireUI) -> str:
  site_name = get_site_name(w, should_exist=False)

  ip = []
  allow_ipv4 = yes_no_menu("Do you want to use IPv4?")
  if allow_ipv4:
    ip.append(_get_ip_network(4))
  allow_ipv6 = yes_no_menu("Do you want to use IPv6?")
  if allow_ipv6:
    ip.append(_get_ip_network(6))

  peer_names = _get_peer_names()

  # Editing of the connection table
  ct = ConnectionTable(peer_names)
  input("Please edit the connection table. Press ENTER to continue...")
  ct = edit_connection_table(ct)

  # Create peer list
  peers = []
  for p in peer_names:
    peers.append(
      get_new_peer_properties(w, site_name, p, ct, allow_ipv4, allow_ipv6))

  try:
    w.add_site(Site(site_name, ip, peers))
  except SiteDoesExistError as e:
    print_error(0, "Site does already exist. Doing nothing...")
    print_error(0, e)

  create_wireguard_config(w, site_name)

  return site_name


def delete_site(w: WireUI):
  site_name = get_site_name(w, should_exist=True)
  if yes_no_menu("Do you really want to delete the site \"" + site_name +
                 "\"?"):
    w.delete_wireguard_config(site_name)
    try:
      w.delete_site(site_name)
    except SiteDoesNotExistError as e:
      print_error(0, "Site does not exist. Doing nothing...")
      print_error(0, e)


def get_site_name(w: WireUI, should_exist: bool) -> str:
  while True:
    name = input("Please enter the name of the site: ")
    exist = w.site_exists(name)
    if (should_exist and exist) or (not should_exist and not exist):
      return name
    elif should_exist and not exist:
      print_error(0, f"Error: {name} does not exist.")
    elif not should_exist and exist:
      print_error(0, f"Error: {name} does already exist.")


# TODO: is correct messages
def _get_ip_network(ip_version: int = 4) -> str:
  while True:
    if ip_version == 4:
      s = "Please enter the IPv4 network the site should use.\n(For example \"10.0.0.0/24\"): "
    else:
      s = "Please enter the IPv6 network the site should use.\n(For example \"fd01::/64\"): "

    ip_network = input(s)

    try:
      ip_network = ipaddress.ip_network(ip_network)
    except ValueError as e:
      print_error(0, "Error: Input is not a valid IP network.")
      print_error(2, e)
    else:
      if ip_version != ip_network.version:
        print_error(
          0, "Error: You entered an IPv" + ip_network.version +
          " network, but an IPv" + ip_version + " network is expected.")
        continue

      return str(ip_network.with_prefixlen)


def _get_peer_names() -> tuple:
  # Get peer names
  peer_names = input(
    "Please enter the name of the peers (use ' ' as separation): ")
  peer_names = _convert_str_to_list(peer_names)

  # Check names
  peer_names = _convert_list_to_str(peer_names)

  correct = False
  while not correct:
    correct = yes_no_menu("Is everything correct?")
    if not correct:
      peer_names = edit_string(peer_names)
      peer_names = _convert_str_to_list(peer_names)
      peer_names = _convert_list_to_str(peer_names)

  peer_names = _convert_str_to_list(peer_names)
  return peer_names


def _convert_str_to_list(peer_names: str) -> list:
  """ Convert a str to a list.

  Doubled entires are removed and the list is sorted. """

  peer_names = list(set(peer_names.split()))
  peer_names.sort()
  return peer_names


def _convert_list_to_str(peer_names: list) -> str:
  """ Convert a list to a str.

  Elements are separated with ' '"""

  print_message(0, "The following peers has been detected:")
  s = ""
  for p in peer_names:
    print_message(0, str(p))
    s += f"{p} "
  s = s[:-1]

  return s
