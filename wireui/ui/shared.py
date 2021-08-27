# shared.py
# Shared functions between sites.py and peers.py
# Author: Tim Schlottmann

import os
import subprocess
import tempfile
from typing import List
from typing import Optional

from .console import print_error
from .console import leave_menu
from .console import options_menu
from .console import print_list
from .console import print_message
from .console import print_header
from .console import yes_no_menu

from .results import get_result_message
from .results import get_connection_table_result_message

from ..library import check_additional_allowed_ips
from ..library import check_endpoint
from ..library import check_port
from ..library import convert_list_to_str
from ..library import convert_str_to_list
from ..library import ConnectionTable
from ..library import JSONDecodeError
from ..library import JsonDict
from ..library import Peer
from ..library import read_file
from ..library import RedirectAllTraffic
from ..library import WireUI

from ..shared import strings


def create_wireguard_config(w: WireUI, site_name: str):
  created_files = w.create_wireguard_config(site_name)
  print_message(1, f"{strings['shared_actions']['create_wg_cfg_list_files']}")
  print_list(created_files)
  print_message(
    0, f"{strings['shared_actions']['create_wg_cfg_files_created']}".format(
      len(created_files)))


def edit_peer_connections(w: WireUI, site_name: str):
  """ Edit the peer connection matrix """

  print_header(f"{strings['shared_actions']['peer_connections_header']}")

  w = WireUI.get_instance()
  ct = get_populated_connection_table(site_name=site_name)

  # Edit table
  input(
    f"{strings['shared_actions']['peer_connections_edit']}\n{strings['misc']['enter_continue']}"
  )
  ct = edit_connection_table(ct)

  leave_menu()

  # Update peers with changed connection table
  for p in w.get_peer_names(site_name=site_name):
    peer_old = w.get_peer(site_name, p)
    allow_ipv4, allow_ipv6, _ = w.get_networks(site_name)

    if (not peer_old.ingoing_connected_peers
        and ct.get_ingoing_connected_peers(p)
        or (not peer_old.outgoing_connected_peers
            and ct.get_outgoing_connected_peers(p))):
      print_header(
        f"{strings['shared_actions']['peer_connections_update_header']}".
        format(p))
      input(
        f"{strings['shared_actions']['peer_connections_collect_infos']}\n{strings['misc']['enter_continue']}"
        .format(p))

    # If a peer now has ingoing connections, ask for endpoint and port
    if not peer_old.ingoing_connected_peers and ct.get_ingoing_connected_peers(
        p):
      if peer_old.endpoint == "":
        endpoint = __get_endpoint(ct.get_ingoing_connected_peers(p))
      else:
        endpoint = peer_old.endpoint
      if peer_old.port == 0:
        port = __get_port(ct.get_ingoing_connected_peers(p))
      else:
        port = peer_old.port
      if peer_old.additional_allowed_ips == []:
        additional_allowed_ips = __get_additional_allowed_ips(
          allow_ipv4, allow_ipv6)
      else:
        additional_allowed_ips = []
      leave_menu()
    else:
      endpoint = peer_old.endpoint
      port = peer_old.port
      additional_allowed_ips = peer_old.additional_allowed_ips

    # If a peer now has outgoing connections, ask for persistent_keep_alive and redirect_all_traffic
    if not peer_old.outgoing_connected_peers and ct.get_outgoing_connected_peers(
        p):
      if peer_old.persistent_keep_alive == -1:
        persistent_keep_alive = __get_persistent_keep_alive()
      else:
        persistent_keep_alive = peer_old.persistent_keep_alive
      redirect_all_traffic = __get_redirect_all_traffic(allow_ipv4, allow_ipv6)
      leave_menu()
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
        peer_old.dns,
        persistent_keep_alive,
        redirect_all_traffic,
        peer_old.post_up,
        peer_old.post_down,
        peer_old.ipv6_routing_fix,
      ))

  create_wireguard_config(w, site_name)


def get_new_peer_properties(w: WireUI, site_name: str, peer_name: str,
                            dns: list, ct: ConnectionTable, allow_ipv4: bool,
                            allow_ipv6: bool) -> Peer:
  print_header(f"{strings['shared_actions']['peer_header']}".format(peer_name))

  input(
    f"{strings['shared_actions']['new_peer_collect_infos']}\n{strings['misc']['enter_continue']}"
    .format(peer_name))

  # If peer has ingoing connections endpoint and port is needed
  if ct.get_ingoing_connected_peers(peer_name):
    endpoint = __get_endpoint(ct.get_ingoing_connected_peers(peer_name))
    port = __get_port(ct.get_ingoing_connected_peers(peer_name))
    additional_allowed_ips = __get_additional_allowed_ips(
      allow_ipv4, allow_ipv6)
  else:
    endpoint = ""
    port = 0
    additional_allowed_ips = []

  # If peer has outgoing connections redirect_all_traffic is needed
  if ct.get_outgoing_connected_peers(peer_name):
    persistent_keep_alive = __get_persistent_keep_alive()
    redirect_all_traffic = __get_redirect_all_traffic(allow_ipv4, allow_ipv6)
  else:
    persistent_keep_alive = -1
    redirect_all_traffic = RedirectAllTraffic(ipv4=False, ipv6=False)

  #Get post up and down
  post_up = __get_post_up()
  post_down = __get_post_down()

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


def change_existing_peer_properties(w: WireUI, site_name: str, peer_name: str,
                                    dns: list, ct: ConnectionTable,
                                    allow_ipv4: bool,
                                    allow_ipv6: bool) -> Peer:
  print_header(f"{strings['shared_actions']['peer_header']}".format(peer_name))

  old_peer = w.get_instance().get_peer(site_name=site_name,
                                       peer_name=peer_name)

  # If peer has ingoing connections endpoint and port is needed
  if ct.get_ingoing_connected_peers(peer_name):
    endpoint = __get_endpoint(ct.get_ingoing_connected_peers(peer_name),
                              old_peer.endpoint)
    port = __get_port(ct.get_ingoing_connected_peers(peer_name), old_peer.port)
    additional_allowed_ips = __get_additional_allowed_ips(
      allow_ipv4, allow_ipv6, old_peer.additional_allowed_ips)
  else:
    endpoint = ""
    port = 0
    additional_allowed_ips = []

  # If peer has outgoing connections redirect_all_traffic is needed
  if ct.get_outgoing_connected_peers(peer_name):
    persistent_keep_alive = __get_persistent_keep_alive(
      old_peer.persistent_keep_alive)
    redirect_all_traffic = __get_redirect_all_traffic(
      allow_ipv4, allow_ipv6, old_peer.redirect_all_traffic)
  else:
    persistent_keep_alive = -1
    redirect_all_traffic = RedirectAllTraffic(ipv4=False, ipv6=False)

  #Get post up and down
  post_up = __get_post_up(old_peer.post_up)
  post_down = __get_post_down(old_peer.post_down)

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


def get_populated_connection_table(site_name: str) -> ConnectionTable:
  w = WireUI.get_instance()
  peer_names = w.get_peer_names(site_name)
  ct = ConnectionTable(peer_names)

  # Populate table with actual data
  for i in range(len(peer_names)):
    peer = w.get_peer(site_name, ct.row_names[i])
    for j in range(len(peer_names)):
      if ct.column_names[j] in peer.outgoing_connected_peers:
        ct.setitem(i, j, 1)
    ct.setitem(i, len(peer_names), peer.main_peer)
  return ct


def __get_endpoint(ingoing_connected_peers: list,
                   old_endpoint: Optional[str] = None) -> str:
  endpoint = old_endpoint
  while True:
    print_header(f"{strings['shared_actions']['endpoint_header']}")
    if endpoint:
      endpoint = input(
        f"{strings['shared_actions']['endpoint_enter']}[{old_endpoint}] "
      ) or old_endpoint
    else:
      endpoint = input(f"{strings['shared_actions']['endpoint_enter']}")
    s = get_result_message(
      check_endpoint(endpoint=endpoint,
                     ingoing_connected_peers=ingoing_connected_peers))
    if s:
      input(s + f"{strings['misc']['enter_retry']}")
      continue
    else:
      break
  leave_menu()
  return endpoint


def __get_port(ingoing_connected_peers: list,
               old_port: Optional[int] = None) -> int:
  while True:
    print_header(f"{strings['shared_actions']['port_header']}")
    if old_port:
      port = input(
        f"{strings['shared_actions']['port_enter']}[{old_port}] ") or old_port
    else:
      port = input(f"{strings['shared_actions']['port_enter']}")
    try:
      port = int(port)
    except ValueError:
      print_error(0, f"{strings['shared_actions']['port_invalid']}")
      continue
    else:
      s = get_result_message(
        check_port(port, ingoing_connected_peers=ingoing_connected_peers))
      if s:
        input(str(s) + f"{strings['misc']['enter_retry']}")
        continue
    leave_menu()
    return port


def __get_persistent_keep_alive(
    old_poersistent_keep_alive: Optional[int] = None) -> int:
  print_header(f"{strings['shared_actions']['nat_header']}")
  if old_poersistent_keep_alive:
    result = yes_no_menu(f"{strings['shared_actions']['nat_yes_no']}", True)
  else:
    result = yes_no_menu(f"{strings['shared_actions']['nat_yes_no']}")
  if result:
    leave_menu()
    return 25
  else:
    leave_menu()
    return 0


def __get_additional_allowed_ips(
    allow_ipv4: bool,
    allow_ipv6: bool,
    old_aaips: Optional[List[str]] = []) -> List[str]:

  aaips = old_aaips
  finished = False
  while not finished:
    if not aaips:
      print_header(f"{strings['shared_actions']['aaips_header']}")
      if not yes_no_menu(f"{strings['shared_actions']['aaips_add_yes_no']}"):
        break
      else:
        print_header()
        aaips = convert_str_to_list(
          input(f"{strings['shared_actions']['aaips_enter']}"))

    print_header(f"{strings['shared_actions']['aaips_header']}")
    print_message(0, f"{strings['shared_actions']['aaips_list']}")
    print_list(aaips)
    correct = yes_no_menu(f"{strings['misc']['correct_yes_no']}")
    if not correct:
      aaips = convert_str_to_list(edit_string(convert_list_to_str(aaips)))

    r = check_additional_allowed_ips(additional_allowed_ips=aaips,
                                     allow_ipv4=allow_ipv4,
                                     allow_ipv6=allow_ipv6)
    s = get_result_message(r)

    if s:
      input(s + f"{strings['misc']['enter_retry']}")
    else:
      break

  leave_menu()
  return aaips


def __get_post_up(old_post_up: Optional[str] = "") -> str:
  post_up = old_post_up
  while True:
    print_header(f"{strings['shared_actions']['post_up_header']}")
    if post_up:
      print_message(
        0, f"{strings['shared_actions']['post_up_actual']}".format(post_up))
      options = {
        "d": f"{strings['shared_actions']['post_up_menu_disable']}",
        "e": f"{strings['shared_actions']['post_up_menu_edit']}",
        "l": f"{strings['shared_actions']['post_up_menu_no_change']}",
      }
      choice = options_menu(options=options)
    else:
      choice = "a"

    if choice == "a":
      post_up = input(f"{strings['shared_actions']['post_up_enter_new']}")
    elif choice == "e":
      post_up = input(
        f"{strings['shared_actions']['post_up_enter_existing']}") or post_up
    elif choice == "d" or choice == "l":
      pass
    if post_up:
      print_message(
        0, f"{strings['shared_actions']['post_up_actual']}".format(post_up))
    else:
      print_message(0, f"{strings['shared_actions']['post_up_disabled']}")

    if yes_no_menu(f"{strings['misc']['correct_yes_no']}"):
      break

  leave_menu()
  return post_up


def __get_post_down(old_post_down: Optional[str] = "") -> str:
  post_down = old_post_down
  while True:
    print_header(f"{strings['shared_actions']['post_down_header']}")
    if post_down:
      print_message(
        0,
        f"{strings['shared_actions']['post_down_actual']}".format(post_down))
      options = {
        "d": f"{strings['shared_actions']['post_down_menu_disable']}",
        "e": f"{strings['shared_actions']['post_down_menu_edit']}",
        "l": f"{strings['shared_actions']['post_down_menu_no_change']}",
      }
      choice = options_menu(options=options)
    else:
      choice = "a"

    if choice == "a":
      post_down = input(f"{strings['shared_actions']['post_down_enter_new']}")
    elif choice == "e":
      post_down = input(
        f"{strings['shared_actions']['post_down_enter_existing']}"
      ) or post_down
    elif choice == "d" or choice == "l":
      pass
    if post_down:
      print_message(
        0,
        f"{strings['shared_actions']['post_down_actual']}".format(post_down))
    else:
      print_message(0, f"{strings['shared_actions']['post_down_disabled']}")

    if yes_no_menu(f"{strings['misc']['correct_yes_no']}"):
      break

  leave_menu()
  return post_down


def __get_redirect_all_traffic(
  allow_ipv4: bool,
  allow_ipv6: bool,
  old_redirect_all_traffic: Optional[RedirectAllTraffic] = None
) -> RedirectAllTraffic:

  print_header(f"{strings['shared_actions']['redirect_traffic_header']}")

  if old_redirect_all_traffic:
    redirect_ipv4 = old_redirect_all_traffic.ipv4
    redirect_ipv6 = old_redirect_all_traffic.ipv6
  else:
    redirect_ipv4 = True
    redirect_ipv6 = True
  if allow_ipv4:
    redirect_ipv4 = yes_no_menu(
      f"{strings['shared_actions']['redirect_traffic_yes_no']}".format("4"),
      redirect_ipv4)
  if allow_ipv6:
    redirect_ipv6 = yes_no_menu(
      f"{strings['shared_actions']['redirect_traffic_yes_no']}".format("6"),
      redirect_ipv6)
  leave_menu()

  return RedirectAllTraffic(redirect_ipv4, redirect_ipv6)


def get_input(msg: str) -> str:
  s = input(msg + ": ")
  while True:
    print_message(0, f"{strings['shared_actions']['input_detect']}\n{s}")
    if yes_no_menu(f"{strings['misc']['correct_yes_no']}"):
      break
    else:
      s = edit_string(s)
      if s:
        s = s[:-1]
  return s


def edit_string(s: str = "") -> str:
  with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as f:
    n = f.name
    f.write(s)

  subprocess.run([WireUI.get_instance().get_setting("editor"), n])
  s = read_file(n)

  os.remove(n)

  return s


def edit_dict(d: JsonDict = JsonDict()) -> JsonDict:
  valid = False
  while not valid:
    try:
      d = JsonDict(edit_string(str(d)))
    except JSONDecodeError:
      pass
    else:
      valid = True
  return d


def edit_connection_table(ct: ConnectionTable) -> ConnectionTable:
  s = ""
  while True:
    r = ct.update(edit_string(str(ct) + "\n" + s))
    s = get_connection_table_result_message(r)
    if r.get_success():
      break

  return ct
