# config.py
# Create and write wireguard config files
# Author: Tim Schlottmann

import ipaddress
import os

from .typedefs import Keys
from .typedefs import PeerItems
from .typedefs import Peers
from .typedefs import SiteItems
from .io_ import delete_directory
from .io_ import prepare_directory
from .io_ import write_file


def write_config(site: SiteItems, wg_config_path: str) -> list:
  """ Create a json config file from the site parameters """

  ip_networks = [ipaddress.ip_network(n) for n in site["ip_networks"]]
  peer_addresses = _get_addresses_for_peers(site["main_peer_name"],
                                            site["peers"], ip_networks)

  prepare_directory(wg_config_path)

  created_files = []
  for p in list(site["peers"]):
    if p == site["main_peer_name"]:
      created_files.append(
          write_file(
              os.path.join(wg_config_path, f"wg_{p}.conf"),
              _get_main_peer_config(
                  peers=site["peers"],
                  endpoint=site["endpoint"],
                  port=site["port"],
                  ip_networks=ip_networks,
                  peer_addresses=peer_addresses,
                  main_peer_name=site["main_peer_name"])))
    else:
      created_files.append(
          write_file(
              os.path.join(wg_config_path, f"wg_{p}.conf"),
              _get_client_peer_config(
                  peers=site["peers"],
                  endpoint=site["endpoint"],
                  port=site["port"],
                  peer_addresses=peer_addresses,
                  main_peer_name=site["main_peer_name"],
                  client_peer_name=p)))
  return created_files


def delete_config(site_name: str, wg_config_path: str):
  """ Delete the config files for a site """

  delete_directory(os.path.join(wg_config_path))


def _get_main_peer_config(peers: Peers, endpoint: str, port: int,
                          ip_networks: ipaddress.ip_network,
                          peer_addresses: dict, main_peer_name: str) -> str:
  """ Write the config file for a server peer """

  s = _get_interface_section(
      interface_peer_name=main_peer_name,
      peer_keys=peers[main_peer_name]["keys"],
      peer_addresses=peer_addresses,
      port=port,
      main_peer=True)
  for p in peers:
    if p != main_peer_name:
      s += _get_peer_section(
          peer_name=p,
          peer_keys=peers[p]["keys"],
          peer_addresses=peer_addresses,
          main_peer=True,
          allow_only_adapter_ip=True)
  return s


def _get_client_peer_config(peers: Peers, endpoint: str, port: int,
                            peer_addresses: dict, main_peer_name: str,
                            client_peer_name: str) -> str:
  """ Write the config file for a client peer """

  s = _get_interface_section(
      interface_peer_name=client_peer_name,
      peer_keys=peers[client_peer_name]["keys"],
      peer_addresses=peer_addresses,
      port=port,
      main_peer=False)
  s += _get_peer_section(
      peer_name=main_peer_name,
      peer_keys=peers[main_peer_name]["keys"],
      peer_addresses=peer_addresses,
      main_peer=False,
      main_peer_keys=peers[client_peer_name]["keys"],
      allow_only_adapter_ip=False,
      endpoint=endpoint,
      port=port)
  return s


def _get_interface_section(interface_peer_name: str, peer_keys: Keys,
                           peer_addresses: dict, port: int,
                           main_peer: bool) -> str:
  """ Get the interface section of a config file """

  s = f"# {interface_peer_name}\n"
  s += f"[Interface]\n"
  s += _get_address_line(interface_peer_name, peer_addresses, main_peer=True)
  if main_peer:
    s += f"ListenPort = {port}\n"
    #TODO: firewall rules
  else:
    s += f"DNS = 1.1.1.1, 8.8.8.8\n"
    #TODO write DNS line
  s += f"PrivateKey = " + peer_keys["privkey"] + "\n"
  s += "\n"
  return s


def _get_peer_section(peer_name: str,
                      peer_keys: Keys,
                      peer_addresses: dict,
                      allow_only_adapter_ip: bool,
                      main_peer: bool,
                      main_peer_keys: dict = {},
                      endpoint: str = "",
                      port: int = 0):
  """ Get the peer section of a config file """

  s = f"# {peer_name}\n"
  s += f"[Peer]\n"
  if not main_peer:
    s += f"Endpoint = {endpoint}:{port}\n"
    s += "PersistentKeepAlive = 25\n"
  s += f"PublicKey = " + peer_keys["pubkey"] + "\n"
  if main_peer:
    s += f"PresharedKey = " + peer_keys["psk"] + "\n"
  else:
    s += f"PresharedKey = " + main_peer_keys["psk"] + "\n"
  s += _get_allowed_ips_line(
      peer_name=peer_name,
      peer_addresses=peer_addresses,
      allow_only_adapter_ip=allow_only_adapter_ip)
  s += "\n"
  return s


def _get_addresses_for_peers(main_peer_name: str, peers: tuple,
                             ip_networks: ipaddress.ip_network):
  """ Create ip addresses for each peer """

  # #Server peer first element. Should get address "1"
  # peer_addresses = {main_peer_name: None}
  peer_addresses = {}
  address_iterators = []
  for n in ip_networks:
    address_iterators.append([n, n.hosts()])
  for p in peers:
    peer_addresses.update({p: {}})
    for i in address_iterators:
      peer_addresses[p].update({i[0]: next(i[1])})
  return peer_addresses


def _get_address_line(peer_name: str, peer_addresses: dict, main_peer: bool):
  """ Create the Address line """

  address_line = "Address = "
  for network in peer_addresses[peer_name].keys():
    address_line += str(peer_addresses[peer_name][network]) + "/" + str(
        network.prefixlen) + ", "

  return address_line[:-2] + "\n"


def _get_allowed_ips_line(peer_name: str, peer_addresses: dict,
                          allow_only_adapter_ip: bool):
  """ Create the AllowedIPs line """

  allowed_ips_line = "AllowedIPs = "
  for network in peer_addresses[peer_name].keys():
    if allow_only_adapter_ip:
      allowed_ips_line += str(peer_addresses[peer_name][network]) + "/" + str(
          network.max_prefixlen) + ", "
    else:
      if network.version == 4:
        allowed_ips_line += "0.0.0.0/0, "
      else:
        allowed_ips_line += "::/0, "

  return allowed_ips_line[:-2] + "\n"
