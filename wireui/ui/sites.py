import ipaddress

from .console import leave_menu
from .console import print_message
from .console import print_error
from .console import print_list
from .console import yes_no_menu
from .console import write_header

from .shared import create_wireguard_config
from .shared import edit_connection_table
from .shared import edit_string
from .shared import get_new_peer_properties

from ..library import ConnectionTable
from ..library import Peer
from ..library import Site
from ..library import SiteDoesExistError
from ..library import SiteDoesNotExistError
from ..library import WireUI


def add_site(w: WireUI) -> str:
  write_header("Add new site")

  site_name = get_site_name(w, should_exist=False)

  ip = []
  ipv4_network = ""
  ipv6_network = ""
  while not ipv4_network and not ipv6_network:
    allow_ipv4, ipv4_network = _get_ip_network(4)
    allow_ipv6, ipv6_network = _get_ip_network(6)
    if not ipv4_network and not ipv6_network:
      write_header("Collecting IP informations")
      input(
        "You have to enter at least one ipv4 or ipv6 network!\nPress ENTER to continue..."
      )
      leave_menu()
  if allow_ipv4:
    ip.append(ipv4_network)
  if allow_ipv6:
    ip.append(ipv6_network)

  dns = _get_dns(w, allow_ipv4, allow_ipv6)

  peer_names = _get_peer_names(w)

  # Editing of the connection table
  ct = ConnectionTable(peer_names)
  input("Please edit the connection table. Press ENTER to continue...")
  ct = edit_connection_table(w, ct)

  # Create peer list
  peers = []
  for p in peer_names:
    peers.append(
      get_new_peer_properties(w, site_name, p, dns, ct, allow_ipv4,
                              allow_ipv6))

  try:
    w.add_site(Site(site_name, ip, dns, peers))
  except SiteDoesExistError as e:
    print_error(0, "Site does already exist. Doing nothing...")
    print_error(0, e)

  create_wireguard_config(w, site_name)

  leave_menu()

  return site_name


def delete_site(w: WireUI):
  write_header("Delete a site")
  site_name = get_site_name(w, should_exist=True)
  if yes_no_menu("Do you really want to delete the site \"" + site_name +
                 "\"?"):
    w.delete_wireguard_config(site_name)
    try:
      w.delete_site(site_name)
    except SiteDoesNotExistError as e:
      print_error(0, "Site does not exist. Doing nothing...")
      print_error(0, e)
  leave_menu()


def get_site_name(w: WireUI, should_exist: bool) -> str:
  while True:
    write_header("Enter site name")
    _list_sites(w)
    name = input("Please enter the name of the site: ")
    exist = w.site_exists(name)
    if (should_exist and exist) or (not should_exist and not exist):
      leave_menu()
      return name
    elif should_exist and not exist:
      print_error(0, f"Error: {name} does not exist.")
    elif not should_exist and exist:
      print_error(0, f"Error: {name} does already exist.")
    leave_menu()


def _list_sites(w: WireUI):
  sites = w.get_sites()
  if sites:
    print_message(0, "The following sites do exist:")
    print_list(sites)
  else:
    print_message(0, "There are currently no sites.")


def _get_ip_network(ip_version: int = 4) -> tuple[bool, str]:
  write_header(f"Collecting IPv{ip_version} informations")
  allow_ip = yes_no_menu(f"Do you want to use IPv{ip_version}?")
  ip_network = ""
  while allow_ip:
    write_header()
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
      continue
    if ip_version != ip_network.version:
      print_error(
        0, "Error: You entered an IPv" + ip_network.version +
        " network, but an IPv" + ip_version + " network is expected.")
      continue
    ip_network = str(ip_network.with_prefixlen)
    break

  leave_menu()

  return (allow_ip, ip_network)


def _get_dns(w: WireUI, allow_ipv4: bool, allow_ipv6: bool) -> list:
  while True:
    write_header("Collecting DNS informations")
    dns = input(
      "Please enter the name of the dns servers (use ' ' as separation): ")
    dns = _convert_str_to_list(dns)
    _check_dns(dns, allow_ipv4, allow_ipv6)
    print_message(0, "The following DNS entries have been detected:")

    correct = False
    while dns and not correct:
      write_header()
      print_list(dns)
      correct = yes_no_menu("Is everything correct?")
      if not correct:
        dns = _convert_list_to_str(dns)
        dns = edit_string(w, dns)
        dns = _convert_str_to_list(dns)
        _check_dns(dns, allow_ipv4, allow_ipv6)
        print_message(0, "The following DNS entries have been detected:")
      if not dns:
        break
    if dns:
      break
  leave_menu()
  return dns


def _check_dns(dns: list, allow_ipv4: bool, allow_ipv6: bool):
  for a in dns:
    try:
      dns_ip_version = ipaddress.ip_address(a).version
    except ValueError:
      dns.remove(a)
    else:
      if (not allow_ipv4 and dns_ip_version == 4) or (not allow_ipv6
                                                      and dns_ip_version == 6):
        remove = yes_no_menu(
          f"DNS Server {a} is IPv{dns_ip_version}, but IPv4 is not allowed.\nThis may not work correctly.\nShould the server be removed?"
        )
        if remove:
          dns.remove(a)


def _get_peer_names(w: WireUI) -> tuple:
  write_header("Collecing peer names")
  # Get peer names
  peer_names = input(
    "Please enter the name of the peers (use ' ' as separation): ")
  peer_names = _convert_str_to_list(peer_names)

  # Check names
  print_message(0, "The following peers has been detected:")

  correct = False
  while not correct:
    write_header()
    print_list(peer_names)
    correct = yes_no_menu("Is everything correct?")
    if not correct:
      peer_names = _convert_list_to_str(peer_names)
      peer_names = edit_string(w, peer_names)
      peer_names = _convert_str_to_list(peer_names)
      print_message(0, "The following peers has been detected:")
  leave_menu()
  return peer_names


def _convert_str_to_list(s: str) -> list:
  """ Convert a str to a list.

  Doubled entires are removed and the list is sorted. """

  s = list(set(s.split()))
  s.sort()
  return s


def _convert_list_to_str(l: list) -> str:
  """ Convert a list to a str.

  Elements are separated with ' '"""

  s = ""
  for e in l:
    s += f"{e} "
  s = s[:-1]

  return s
