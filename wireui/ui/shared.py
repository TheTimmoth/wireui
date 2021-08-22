# shared.py
# Shared functions between sites.py and peers.py
# Author: Tim Schlottmann

import ipaddress
import os
import subprocess
import tempfile

from .console import leave_menu
from .console import print_error
from .console import print_list
from .console import print_message
from .console import write_header
from .console import yes_no_menu

from ..library import check_endpoint
from ..library import check_port
from ..library import ConnectionTable
from ..library import EndpointError
from ..library import JSONDecodeError
from ..library import JsonDict
from ..library import Peer
from ..library import PortError
from ..library import read_file
from ..library import RedirectAllTraffic
from ..library import WireUI


def create_wireguard_config(w: WireUI, site_name: str):
  created_files = w.create_wireguard_config(site_name)
  print_message(1, "The following files have been created:")
  print_list(created_files)
  print_message(0, f"{len(created_files)} file(s) have been created.")


def get_new_peer_properties(w: WireUI, site_name: str, peer_name: str,
                            dns: list, ct: ConnectionTable, allow_ipv4: bool,
                            allow_ipv6: bool) -> Peer:
  write_header(f"Peer {peer_name}")
  input(
    f"Collecting information for peer {peer_name}.\nPress ENTER to continue..."
  )

  # If peer has ingoing connections endpoint and port is needed
  if ct.get_ingoing_connected_peers(peer_name):
    endpoint = get_endpoint(ct.get_ingoing_connected_peers(peer_name))
    port = get_port(ct.get_ingoing_connected_peers(peer_name))
    additional_allowed_ips = get_additional_allowed_ips(allow_ipv4, allow_ipv6)
  else:
    endpoint = ""
    port = 0
    additional_allowed_ips = []

  # If peer has outgoing connections redirect_all_traffic is needed
  if ct.get_outgoing_connected_peers(peer_name):
    persistent_keep_alive = get_persistent_keep_alive()
    redirect_all_traffic = get_redirect_all_traffic(allow_ipv4, allow_ipv6)
  else:
    persistent_keep_alive = -1
    redirect_all_traffic = RedirectAllTraffic(ipv4=False, ipv6=False)

  #Get post up and down
  post_up = get_post_up()
  post_down = get_post_down()

  #ipv6_routing_fix
  ipv6_routing_fix = False

  leave_menu()

  return Peer(
    peer_name,
    additional_allowed_ips,
    ct.get_outgoing_connected_peers(peer_name),
    ct.get_main_peer(peer_name),
    ct.get_ingoing_connected_peers(peer_name),
    endpoint,
    port,
    dns,
    persistent_keep_alive,
    redirect_all_traffic,
    post_up,
    post_down,
    ipv6_routing_fix,
  )


def get_endpoint(ingoing_connected_peers: list) -> str:
  while True:
    write_header("Getting endpoint address")
    endpoint = input("Please enter the URL or IP address of the server: ")
    try:
      check_endpoint(endpoint=endpoint,
                     ingoing_connected_peers=ingoing_connected_peers)
    except EndpointError as e:
      input(str(e) + "\nPress Enter to continue...")
      continue
    else:
      break
  leave_menu()
  return endpoint


def get_port(ingoing_connected_peers: list) -> int:
  while True:
    write_header("Enter port number")
    port = input("Please enter the port the adapter should listen on: ")
    try:
      port = int(port)
    except ValueError:
      print_error(0, "Error: The port was not a valid integer.")
      continue
    else:
      try:
        check_port(port, ingoing_connected_peers=ingoing_connected_peers)
      except PortError as e:
        input(str(e) + "\nPress Enter to continue...")
        continue
    leave_menu()
    return port


def get_persistent_keep_alive() -> int:
  write_header("NAT")
  if yes_no_menu("Is the peer behind a NAT?"):
    leave_menu()
    return 25
  else:
    leave_menu()
    return 0


def get_additional_allowed_ips(allow_ipv4: bool, allow_ipv6: bool) -> list:
  l = []
  write_header("Additional routable IPs")
  if yes_no_menu("Do you want to add an additional AllowedIP network?"):
    while True:
      write_header()
      while True:
        write_header()
        try:
          a = ipaddress.ip_network(
            input(
              "Please enter an additional ip network to add to the AllowedIPs List: "
            ))
        except ValueError as e:
          print_error(0, "Error: Input is not a valid IP network.")
          print_error(2, e)
        else:
          if not allow_ipv4 and a.version == 4:
            print_message(
              0, "IPv6 only network. An IPv4 address is not allowed!")
          elif not allow_ipv6 and a.version == 6:
            print_message(
              0, "IPv4 only network. An IPv6 address is not allowed!")
          else:
            break

      l.append(str(a.with_prefixlen))

      if yes_no_menu("Do you want to add another network?"):
        continue
      else:
        break

  leave_menu()
  return l


def get_post_up() -> str:
  post_up = ""
  write_header("PostUp")
  if yes_no_menu("Do you want to add a PostUp command?"):
    post_up = get_input("Please enter the PostUp command")
  leave_menu()
  return post_up


def get_post_down() -> str:
  post_down = ""
  write_header("PostDown")
  if yes_no_menu("Do you want to add a PostDown command?"):
    post_down = get_input("Please enter the PostDown command")
  leave_menu()
  return post_down


def get_redirect_all_traffic(allow_ipv4: bool,
                             allow_ipv6: bool) -> RedirectAllTraffic:
  write_header("Redirect traffic")
  redirect_ipv4 = False
  redirect_ipv6 = False
  if allow_ipv4:
    redirect_ipv4 = yes_no_menu(
      "Please enter if all IPv4 traffic from this peer should be redirected:")
  if allow_ipv6:
    redirect_ipv6 = yes_no_menu(
      "Please enter if all IPv6 traffic from this peer should be redirected:")
  leave_menu()
  return RedirectAllTraffic(redirect_ipv4, redirect_ipv6)


def get_input(msg: str) -> str:
  s = input(msg + ": ")
  while True:
    print_message(0, f"Detected the following:\n{s}")
    if yes_no_menu("Is this correct?"):
      break
    else:
      s = edit_string(s)
      if s:
        s = s[:-1]
  return s


def edit_string(w: WireUI, s: str = "") -> str:
  with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as f:
    n = f.name
    f.write(s)

  subprocess.run([w.get_setting("editor"), n])
  s = read_file(n)

  os.remove(n)

  return s


def edit_dict(w: WireUI, d: JsonDict = JsonDict()) -> JsonDict:
  valid = False
  while not valid:
    try:
      d = JsonDict(edit_string(w, str(d)))
    except JSONDecodeError:
      pass
    else:
      valid = True
  return d


def edit_connection_table(w: WireUI, ct: ConnectionTable) -> ConnectionTable:
  s = ""
  valid = False
  while not valid:
    try:
      ct.update(edit_string(w, str(ct) + s))
    except ValueError as e:
      s = f"\n{e}"
    else:
      valid = True
  return ct
