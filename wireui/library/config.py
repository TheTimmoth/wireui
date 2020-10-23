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

  peer_addresses = _get_addresses_for_peers(site["peers"],
                                            [ipaddress.ip_network(n) for n in site["ip_networks"]])

  prepare_directory(wg_config_path)

  created_files = []
  for p in site["peers"]:
    created_files.append(
        write_file(
            os.path.join(wg_config_path, f"wg_{p}.conf"),
            _get_peer_config(p, site["peers"], peer_addresses)))
  return created_files


def delete_config(site_name: str, wg_config_path: str):
  """ Delete the config files for a site """

  delete_directory(os.path.join(wg_config_path))


def _get_peer_config(interface_peer_name: str, peers: Peers, peer_addresses: dict):
  """ Write config file for a peer """
  s = _get_interface_section(interface_peer_name, peers[interface_peer_name], peer_addresses)

  for p in peers:
    if p != interface_peer_name and ((p in peers[interface_peer_name]["ingoing_connected_peers"]) or (p in peers[interface_peer_name]["outgoing_connected_peers"])):
      s += _get_peer_section(p, peers[p], interface_peer_name, peers[interface_peer_name], peer_addresses)

  return s


def _get_interface_section(name: str, peer: PeerItems, peer_addresses: dict) -> str:
  """ Get the interface section of a config file for a peer"""

  s = f"# {name}\n"
  s += "[Interface]\n"
  s += _get_address_line(name, peer_addresses)
  if peer["ingoing_connected_peers"]:
    s += f"ListenPort = {peer['port']}\n"
    #TODO: firewall rules
  if peer["redirect_all_traffic"]:
    s += f"DNS = 1.1.1.1, 8.8.8.8\n"
  s += f"PrivateKey = " + peer["keys"]["privkey"] + "\n"
  s += "\n"
  return s


def _get_peer_section(name: str, peer: PeerItems, interface_peer_name: str, interface_peer: PeerItems, peer_addresses: dict):
  """ Get the peer section of a config file """

  s = f"# {name}\n"
  s += f"[Peer]\n"
  if peer["endpoint"] and name in interface_peer["outgoing_connected_peers"]:
    s += f"Endpoint = {peer['endpoint']}:{peer['port']}\n"
    if peer["persistent_keep_alive"]:
      s += "PersistentKeepAlive = 25\n"
  s += f"PublicKey = " + peer["keys"]["pubkey"] + "\n"

  # Always the psk of the outgoing_connected_peers is used
  # If a peer is ingoing and outgoing the psk of the alphebetically first peer is used
  if name in interface_peer["ingoing_connected_peers"] and name in interface_peer["outgoing_connected_peers"]:
    l = [name, interface_peer_name]
    l.sort()
    if name == l[0]:
      s += f"PresharedKey = " + peer["keys"]["psk"] + "\n"
    else:
      s += f"PresharedKey = " + interface_peer["keys"]["psk"] + "\n"
  elif name in interface_peer["ingoing_connected_peers"]:
    s += f"PresharedKey = " + peer["keys"]["psk"] + "\n"
  else:
    # Peer has to be outgoing_connected_peer
    s += f"PresharedKey = " + interface_peer["keys"]["psk"] + "\n"
  s += _get_allowed_ips_line(
      peer_name=name,
      peer=peer,
      interface_peer=interface_peer,
      peer_addresses=peer_addresses,
      redirect_all_traffic=interface_peer["redirect_all_traffic"])
  s += "\n"
  return s


def _get_addresses_for_peers(peers: tuple,
                             ip_networks: list):
  """ Create ip addresses for each peer """

  peer_addresses = {}
  address_iterators = []
  for n in ip_networks:
    address_iterators.append([n, n.hosts()])
  for p in peers:
    peer_addresses.update({p: {}})
    for i in address_iterators:
      peer_addresses[p].update({i[0]: next(i[1])})
  return peer_addresses


def _get_address_line(peer_name: str, peer_addresses: dict):
  """ Create the Address line """

  address_line = "Address = "
  for network in peer_addresses[peer_name].keys():
    address_line += str(peer_addresses[peer_name][network]) + "/" + str(
        network.prefixlen) + ", "

  return address_line[:-2] + "\n"


def _get_allowed_ips_line(peer_name: str, peer: PeerItems, interface_peer: PeerItems, peer_addresses: dict,
                          redirect_all_traffic: bool):
  """ Create the AllowedIPs line """

  allowed_ips_line = "AllowedIPs = "
  for network in peer_addresses[peer_name].keys():
    if redirect_all_traffic and peer_name in interface_peer["main_peer"]:
      if network.version == 4:
        allowed_ips_line += "0.0.0.0/0, "
      else:
        allowed_ips_line += "::/0, "
    else:
      allowed_ips_line += str(peer_addresses[peer_name][network]) + "/" + str(
          network.max_prefixlen) + ", "
    for s in peer["additional_allowed_ips"]:
      allowed_ips_line += s + ", "


  return allowed_ips_line[:-2] + "\n"
