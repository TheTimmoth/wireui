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
from .shared import edit_peer_connections
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

from ..shared import strings


class __IPNetworks(NamedTuple):
  allow_ipv4: bool
  allow_ipv6: bool
  ip_networks: List[str]


def add_site(w: WireUI) -> str:
  print_header(f"{strings['site_actions']['add_site_header']}")

  site_name = get_site_name(w, should_exist=False)

  allow_ipv4, allow_ipv6, ip = __get_ip_networks()

  dns = __get_dns(w, allow_ipv4, allow_ipv6)

  peer_names = __get_peer_names(w)

  # Editing of the connection table
  ct = ConnectionTable(peer_names)
  input(
    f"{strings['site_actions']['add_site_connection_table']}\n{strings['misc']['enter_continue']}"
  )
  ct = edit_connection_table(ct)

  # Create peer list
  peers = []
  for p in peer_names:
    peers.append(
      get_new_peer_properties(w, site_name, p, dns, ct, allow_ipv4,
                              allow_ipv6))

  w.add_site(Site(site_name, ip, dns, peers))

  create_wireguard_config(w, site_name)

  leave_menu()

  return site_name


def edit_site():
  print_header(f"{strings['site_actions']['edit_site_header']}")
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

  w.set_site(
    Site(name=site_name, ip_networks=ip_networks, dns=dns, peers=s.peers))

  if yes_no_menu(
      f"{strings['site_actions']['edit_site_connection_table_yes_no']}",
      False):
    edit_peer_connections(w, site_name)

  create_wireguard_config(w, site_name)

  print_header()
  if yes_no_menu(
      f"{strings['site_actions']['edit_site_peer_properties_yes_no']}", False):
    leave_menu()
    edit_peer(site_name)

  leave_menu()


def delete_site(w: WireUI):
  print_header(f"{strings['site_actions']['delete_header']}")
  site_name = get_site_name(w, should_exist=True)
  if yes_no_menu(
      f"{strings['site_actions']['delete_yes_no']}".format(site_name)):
    w.delete_wireguard_config(site_name)
    w.delete_site(site_name)
  leave_menu()


def get_site_name(w: WireUI, should_exist: bool) -> str:
  while True:
    print_header(f"{strings['site_actions']['site_name_header']}")
    __list_sites(w)
    name = input(f"{strings['site_actions']['site_name_enter']}")
    exist = w.site_exists(name)
    if (should_exist and exist) or (not should_exist and not exist):
      leave_menu()
      return name
    elif should_exist and not exist:
      print_error(
        0, f"{strings['site_actions']['site_name_not_exists_error']}".format(
          name))
    elif not should_exist and exist:
      print_error(
        0, f"{strings['site_actions']['site_name_exists_error']}".format(name))
    input(f"{strings['misc']['enter_continue']}")
    leave_menu()


def __list_sites(w: WireUI):
  sites = w.get_sites()
  if sites:
    print_message(0, f"{strings['site_actions']['list_site']}")
    print_list(sites)
  else:
    print_message(0, f"{strings['site_actions']['list_site_empty']}")


def __get_ip_networks(old_ip_networks: Optional[__IPNetworks] = __IPNetworks(
  True, True, [])) -> __IPNetworks:

  print_header(f"{strings['site_actions']['ip_networks_header']}")

  allow_ip = {
    4: old_ip_networks.allow_ipv4,
    6: old_ip_networks.allow_ipv6,
  }
  ip_networks = old_ip_networks.ip_networks

  for v in [4, 6]:
    print_header(
      f"{strings['site_actions']['ip_networks_version_header']}".format(v))
    allow_ip[v] = yes_no_menu(
      f"{strings['site_actions']['ip_networks_yes_no']}?".format(v),
      allow_ip[v])

    default = ""
    for n in ip_networks:
      if ipaddress.ip_network(n).version == v:
        default = n
        ip_networks.remove(n)

    while allow_ip[v]:
      print_header()

      if default:
        s = f"{strings['site_actions']['ip_networks_enter_default']}".format(
          v, default)
        ip_networks.append(input(s) or default)
      else:
        if v == 4:
          example = "10.0.0.0/24"
        else:
          example = "fd01::/64"
        s = f"{strings['site_actions']['ip_networks_enter']}".format(
          v, example)
        ip_networks.append(input(s))

      r, _, _ = check_ip_networks(ip_networks)
      s = get_result_message(r)
      if s:
        input(s + f"{strings['misc']['enter_retry']}")
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
    print_header(f"{strings['site_actions']['dns_header']}")
    correct = False
    if not dns:
      dns = convert_str_to_list(
        input(f"{strings['site_actions']['dns_enter']}"))
    else:
      print_message(0, f"{strings['site_actions']['dns_list']}")
      print_list(dns)
      correct = yes_no_menu(f"{strings['misc']['correct_yes_no']}")
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
        input(s + f"{strings['misc']['enter_continue']}")
      else:
        correct = True
  leave_menu()
  return dns


def __get_peer_names(w: WireUI) -> Tuple[str, ...]:
  print_header("Collecing peer names")
  # Get peer names
  peer_names = convert_str_to_list(
    input(f"{strings['site_actions']['peer_names_header']}"))

  correct = False
  while not correct:
    print_header()
    print_list(peer_names)
    correct = yes_no_menu(f"{strings['misc']['correct_yes_no']}")
    if not correct:
      peer_names = convert_str_to_list(
        edit_string(convert_list_to_str(peer_names)))
      print_message(0, f"{strings['site_actions']['peer_list']}")
  leave_menu()
  return peer_names
