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

  peer_addresses = __get_addresses_for_peers(
    site["peers"], [ipaddress.ip_network(n) for n in site["ip_networks"]])

  prepare_directory(wg_config_path)

  created_files = []
  for p in site["peers"]:
    created_files.append(
      write_file(os.path.join(wg_config_path, f"wg_{p}.conf"),
                 __get_peer_config(p, site["peers"], peer_addresses)))
  return created_files


def delete_config(site_name: str, wg_config_path: str):
  """ Delete the config files for a site """

  delete_directory(os.path.join(wg_config_path))


def __get_peer_config(interface_peer_name: str, peers: Peers,
                      peer_addresses: dict):
  """ Write config file for a peer """
  s = __get_interface_section(interface_peer_name, peers[interface_peer_name],
                              peer_addresses)

  for p in peers:
    if p != interface_peer_name and (
      (p in peers[interface_peer_name]["ingoing_connected_peers"]) or
      (p in peers[interface_peer_name]["outgoing_connected_peers"])):
      s += __get_peer_section(p, peers[p], interface_peer_name,
                              peers[interface_peer_name], peer_addresses)

  return s


def __get_interface_section(name: str, peer: PeerItems,
                            peer_addresses: dict) -> str:
  """ Get the interface section of a config file for a peer"""

  s = f"# {name}\n"
  s += "[Interface]\n"
  s += __get_address_line(name, peer_addresses)
  if peer["ingoing_connected_peers"]:
    s += f"ListenPort = {peer['port']}\n"
  # TODO: firewall rules
  if peer["redirect_all_traffic"]:
    if peer["redirect_all_traffic"]["ipv4"] and peer["redirect_all_traffic"][
        "ipv6"]:
      if peer["dns"]:
        s += f"DNS = "
        for a in peer["dns"]:
          s += f"{a}, "
        s = s[:-2] + "\n"
      else:
        s += f"DNS = 1.1.1.1, 8.8.8.8\n"
  s += f"PrivateKey = " + peer["keys"]["privkey"] + "\n"

  post_up = ""
  post_down = ""
  if peer["ipv6_routing_fix"]:
    for network in peer_addresses[name]:
      if peer_addresses[name][network].version == 6:
        post_up += f"ip -6 rule add from {peer_addresses[name][network]} table 501; ip -6 route add default via {peer_addresses[peer['main_peer']][network]} table 501; ip -6 rule delete table 51820; ip -6 rule delete table main suppress_prefixlength 0;"
        break
    post_down += "ip -6 rule delete table 501;"
    post_up += " "
    post_down += " "
  post_up += peer["post_up"]
  post_down += peer["post_down"]
  if post_up:
    s += f"PostUp = {post_up}\n"
  if post_down:
    s += f"PostDown = {post_down}\n"
  s += "\n"
  return s


def __get_peer_section(name: str, peer: PeerItems, interface_peer_name: str,
                       interface_peer: PeerItems, peer_addresses: dict):
  """ Get the peer section of a config file """

  s = f"# {name}\n"
  s += f"[Peer]\n"
  if peer["endpoint"] and name in interface_peer["outgoing_connected_peers"]:
    s += f"Endpoint = {peer['endpoint']}:{peer['port']}\n"
    if interface_peer["persistent_keep_alive"] == 25:
      s += "PersistentKeepAlive = 25\n"
  s += f"PublicKey = " + peer["keys"]["pubkey"] + "\n"

  # Always the psk of the outgoing_connected_peers is used
  # If a peer is ingoing and outgoing the psk of the alphebetically first peer is used
  if name in interface_peer[
      "ingoing_connected_peers"] and name in interface_peer[
        "outgoing_connected_peers"]:
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
  s += __get_allowed_ips_line(
    peer_name=name,
    peer=peer,
    interface_peer=interface_peer,
    peer_addresses=peer_addresses,
  )
  s += "\n"
  return s


def __get_addresses_for_peers(peers: tuple, ip_networks: list):
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


def __get_address_line(peer_name: str, peer_addresses: dict):
  """ Create the Address line """

  address_line = "Address = "
  for network in peer_addresses[peer_name].keys():
    address_line += str(peer_addresses[peer_name][network]) + "/" + str(
      network.prefixlen) + ", "

  return address_line[:-2] + "\n"


def __get_allowed_ips_line(peer_name: str, peer: PeerItems,
                           interface_peer: PeerItems, peer_addresses: dict):
  """ Create the AllowedIPs line """

  allowed_ips_line = "AllowedIPs = "
  for network in peer_addresses[peer_name].keys():
    if peer_name == interface_peer[
        "main_peer"] and network.version == 4 and interface_peer[
          "redirect_all_traffic"]["ipv4"]:
      allowed_ips_line += "0.0.0.0/0, "
    elif peer_name == interface_peer["main_peer"] and network.version == 6 and (
        interface_peer["redirect_all_traffic"]["ipv6"]
        or interface_peer["ipv6_routing_fix"]):
      allowed_ips_line += "::/0, "
    else:
      allowed_ips_line += str(peer_addresses[peer_name][network]) + "/" + str(
        network.max_prefixlen) + ", "
  for s in peer["additional_allowed_ips"]:
    allowed_ips_line += s + ", "

  return allowed_ips_line[:-2] + "\n"
