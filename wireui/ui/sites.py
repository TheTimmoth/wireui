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

from ..library import check_dns
from ..library import check_ip_networks
from ..library import convert_list_to_str
from ..library import convert_str_to_list
from ..library import ConnectionTable
from ..library import DNSError
from ..library import IPNetworkError
from ..library import Site
from ..library import SiteDoesExistError
from ..library import SiteDoesNotExistError
from ..library import WireUI


def add_site(w: WireUI) -> str:
  write_header("Add new site")

  site_name = get_site_name(w, should_exist=False)

  allow_ipv4, allow_ipv6, ip = __get_ip_networks()

  dns = __get_dns(w, allow_ipv4, allow_ipv6)

  peer_names = __get_peer_names(w)

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


def __get_ip_networks() -> tuple[bool, bool, list]:
  write_header(f"Collecting IP information")
  allow_ip = {}
  ip_networks = []
  for v in [4, 6]:
    write_header(f"IPv{v}")
    allow_ip[v] = yes_no_menu(f"Do you want to use IPv{v}?")
    while allow_ip[v]:
      write_header()
      if v == 4:
        s = "Please enter the IPv4 network the site should use.\n(For example \"10.0.0.0/24\"): "
      else:
        s = "Please enter the IPv6 network the site should use.\n(For example \"fd01::/64\"): "

      ip_networks.append(input(s))

      try:
        check_ip_networks(ip_networks)
      except IPNetworkError as e:
        ip_networks.pop()
        input(str(e) + "\n Press ENTER to retry...")
        continue
      else:
        leave_menu()
        break

  leave_menu()

  if not ip_networks:
    allow_ip[4], allow_ip[6], ip_networks = __get_ip_networks()

  return (allow_ip[4], allow_ip[6], ip_networks)


def __get_dns(w: WireUI, allow_ipv4: bool, allow_ipv6: bool) -> list:
  correct = False
  dns = []
  while not dns or not correct:
    write_header("Collecting DNS informations")
    if not dns:
      dns = input(
        "Please enter the name of the dns servers (use ' ' as separation): ")
      dns = convert_str_to_list(dns)

      for a in dns:
        try:
          check_dns(dns=[a], allow_ipv4=allow_ipv4, allow_ipv6=allow_ipv6)
        except DNSError as e:
          input(str(e) + "\nPress Enter to continue...")
          dns.remove(a)
    else:
      print_message(0, "The following DNS entries have been detected:")
      print_list(dns)
      correct = yes_no_menu("Is everything correct?")
      if not correct:
        dns = convert_list_to_str(dns)
        dns = edit_string(w, dns)
        dns = convert_str_to_list(dns)
      if not dns:
        break
    if dns:
      break
  leave_menu()
  return dns


def __get_peer_names(w: WireUI) -> tuple:
  write_header("Collecing peer names")
  # Get peer names
  peer_names = input(
    "Please enter the name of the peers (use ' ' as separation): ")
  peer_names = convert_str_to_list(peer_names)

  # Check names
  print_message(0, "The following peers has been detected:")

  correct = False
  while not correct:
    write_header()
    print_list(peer_names)
    correct = yes_no_menu("Is everything correct?")
    if not correct:
      peer_names = convert_list_to_str(peer_names)
      peer_names = edit_string(w, peer_names)
      peer_names = convert_str_to_list(peer_names)
      print_message(0, "The following peers has been detected:")
  leave_menu()
  return peer_names
