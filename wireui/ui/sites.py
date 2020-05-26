import ipaddress

from .console import print_message
from .console import print_error

from ..library import Site
from ..library import SiteDoesExistError
from ..library import SiteDoesNotExistError
from ..library import WireUI

from .shared import yes_no_menu


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
  if yes_no_menu("Do you want to use IPv4?"):
    ip.append(_get_ip_network(4))
  if yes_no_menu("Do you want to use IPv6?"):
    ip.append(_get_ip_network(6))

  endpoint = _get_endpoint()

  port = _get_port()

  main_peer_name, client_peer_names = _get_peer_names()

  try:
    w.add_site(
        Site(site_name, endpoint, port, ip, main_peer_name, client_peer_names))
  except SiteDoesExistError as e:
    print_error(0, "Site does already exist. Doing nothing...")
    print_error(0, e)

  w.create_wireguard_config(site_name)

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


def _get_endpoint() -> str:
  return input("Please enter the URL or IP address of the server: ")


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


def _get_port() -> int:
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


def _get_peer_names() -> tuple:
  main_peer_name = input("Please enter the name of the server peer: ")

  client_peer_names = []
  name = None
  while name != "":
    name = input(
        "Please enter the name of one client peer. (Leave empty when you have finished) "
    )
    if name == main_peer_name or name in client_peer_names:
      print_error(0, "Error: The given name does already exist. Continuing...")
    elif name != "":
      client_peer_names.append(name)
  return main_peer_name, client_peer_names
