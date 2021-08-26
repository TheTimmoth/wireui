import ipaddress
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Tuple

from .console import leave_menu
from .console import print_message
from .console import print_error
from .console import print_list
from .console import yes_no_menu
from .console import print_header

from .peers import edit_peer

from .results import get_result_message

from .shared import create_wireguard_config
from .shared import edit_connection_table
from .shared import edit_string
from .shared import get_new_peer_properties

from ..library import check_dns
from ..library import check_ip_networks
from ..library import convert_list_to_str
from ..library import convert_str_to_list
from ..library import get_default_dns
from ..library import ConnectionTable
from ..library import Site
from ..library import SiteDoesExistError
from ..library import SiteDoesNotExistError
from ..library import WireUI


class __IPNetworks(NamedTuple):
  allow_ipv4: bool
  allow_ipv6: bool
  ip_networks: List[str]


def add_site(w: WireUI) -> str:
  print_header("Add new site")

  site_name = get_site_name(w, should_exist=False)

  allow_ipv4, allow_ipv6, ip = __get_ip_networks()

  dns = __get_dns(w, allow_ipv4, allow_ipv6)

  peer_names = __get_peer_names(w)

  # Editing of the connection table
  ct = ConnectionTable(peer_names)
  input("Please edit the connection table. Press ENTER to continue...")
  ct = edit_connection_table(ct)

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


def edit_site():
  print_header("Edit site")
  w = WireUI.get_instance()

  site_name = get_site_name(w, True)
  peer_names = w.get_peer_names(site_name)

  s = w.get_site(site_name)

  # Get IP networks
  ip_networks = s.ip_networks
  allow_ipv4 = False
  allow_ipv6 = False
  for n in ip_networks:
    v = ipaddress.ip_network(n).version
    if v == 4:
      allow_ipv4 = True
    else:
      allow_ipv6 = True

  # Get IP networks
  allow_ipv4, allow_ipv6, ip = __get_ip_networks(
    __IPNetworks(allow_ipv4, allow_ipv6, ip_networks))

  # Get DNS
  dns = __get_dns(w, allow_ipv4, allow_ipv6, s.dns)

  # Edit connection table
  # TODO: should this be possible here?
  # if yes_no_menu("Do you want to edit the connection table?", False):
  #   edit_peer_connections(w, site_name)

  w.set_site(
    Site(name=site_name, ip_networks=ip_networks, dns=dns, peers=s.peers))

  create_wireguard_config(w, site_name)

  print_header()
  if yes_no_menu("Do you want to edit peer properties?", False):
    leave_menu()
    edit_peer(site_name)

  leave_menu()


def delete_site(w: WireUI):
  print_header("Delete a site")
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
    print_header("Enter site name")
    __list_sites(w)
    name = input("Please enter the name of the site: ")
    exist = w.site_exists(name)
    if (should_exist and exist) or (not should_exist and not exist):
      leave_menu()
      return name
    elif should_exist and not exist:
      print_error(0, f"Error: {name} does not exist.")
    elif not should_exist and exist:
      print_error(0, f"Error: {name} does already exist.")
    input("Press ENTER to continue...")
    leave_menu()


def __list_sites(w: WireUI):
  sites = w.get_sites()
  if sites:
    print_message(0, "The following sites do exist:")
    print_list(sites)
  else:
    print_message(0, "There are currently no sites.")


def __get_ip_networks(old_ip_networks: Optional[__IPNetworks] = __IPNetworks(
  True, True, [])) -> __IPNetworks:

  print_header(f"Collecting IP information")

  allow_ip = {
    4: old_ip_networks.allow_ipv4,
    6: old_ip_networks.allow_ipv6,
  }
  ip_networks = old_ip_networks.ip_networks

  for v in [4, 6]:
    print_header(f"IPv{v}")
    allow_ip[v] = yes_no_menu(f"Do you want to use IPv{v}?", allow_ip[v])

    default = ""
    for n in ip_networks:
      if ipaddress.ip_network(n).version == v:
        default = n
        ip_networks.remove(n)

    while allow_ip[v]:
      print_header()

      if default:
        if v == 4:
          s = f"Please enter the IPv4 network the site should use: [{default}] "
        else:
          s = f"Please enter the IPv6 network the site should use: [{default}] "
        ip_networks.append(input(s) or default)
      else:
        if v == 4:
          s = "Please enter the IPv4 network the site should use. (For example \"10.0.0.0/24\"): "
        else:
          s = "Please enter the IPv6 network the site should use. (For example \"fd01::/64\"): "
        ip_networks.append(input(s))

      r, _, _ = check_ip_networks(ip_networks)
      s = get_result_message(r)
      if s:
        input(s + "Press ENTER to retry...")
        continue
      else:
        break

    leave_menu()

  leave_menu()

  if not ip_networks:
    allow_ip[4], allow_ip[6], ip_networks = __get_ip_networks()

  return __IPNetworks(allow_ip[4], allow_ip[6], ip_networks)


def __get_dns(w: WireUI,
              allow_ipv4: bool,
              allow_ipv6: bool,
              old_dns: Optional[List[str]] = []) -> List[str]:
  correct = False
  dns = old_dns or get_default_dns(allow_ipv4=allow_ipv4,
                                   allow_ipv6=allow_ipv6)
  while not dns or not correct:
    print_header("Collecting DNS informations")
    correct = False
    if not dns:
      dns = convert_str_to_list(
        input(
          "Please enter the name of the dns servers (use ' ' as separation): ")
      )
    else:
      print_message(0, "The following DNS entries are set:")
      print_list(dns)
      correct = yes_no_menu("Is everything correct?")
      if not correct:
        dns = convert_str_to_list(edit_string(convert_list_to_str(dns)))
    if dns:
      print_header()
      s = get_result_message(
        check_dns(dns=dns,
                  allow_ipv4=allow_ipv4,
                  allow_ipv6=allow_ipv6,
                  default_dns=[]))
      if s:
        input(s + "Press ENTER to continue...")
      else:
        correct = True
  leave_menu()
  return dns


def __get_peer_names(w: WireUI) -> Tuple[str, ...]:
  print_header("Collecing peer names")
  # Get peer names
  peer_names = input(
    "Please enter the name of the peers (use ' ' as separation): ")
  peer_names = convert_str_to_list(peer_names)

  # Check names
  print_message(0, "The following peers has been detected:")

  correct = False
  while not correct:
    print_header()
    print_list(peer_names)
    correct = yes_no_menu("Is everything correct?")
    if not correct:
      peer_names = convert_str_to_list(
        edit_string(convert_list_to_str(peer_names)))
      print_message(0, "The following peers has been detected:")
  leave_menu()
  return peer_names
