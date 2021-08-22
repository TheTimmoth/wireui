# integrity.py
# Check program existence and integrity from imported data
# Author: Tim Schlottmann

import os
import re
import ipaddress

from .keys import get_keys

from .typedefs import AdditionalAllowedIPError
from .typedefs import DataIntegrityError
from .typedefs import DNSError
from .typedefs import EndpointError
from .typedefs import IPNetworkError
from .typedefs import PeerConnectionError
from .typedefs import PeerItems
from .typedefs import Peers
from .typedefs import PortError
from .typedefs import RedirectAllTraffic
from .typedefs import Settings
from .typedefs import SiteItems
from .typedefs import Sites

version_dict = {
  "0.1.0": 1,
  "0.1.1": 2,
  "0.1.2": 3,
  "0.1.3": 4,
}

settings_latest_version = "0.1.1"
site_latest_version = "0.1.3"


def check_wireguard():
  get_keys()


# Data check recipe
#
# A check is done after the following recipe:
# 1. Check if a key is present
# 2. Check if the value has the correct datatype
# 3. If the value is of type list or dict repeat step 2
# 4. Make additional checks where applicable


def check_imported_sites(sites: Sites) -> Sites:
  """ Check data integrity of the sites """
  for s in sites:
    # Check config_version
    __check_key(sites[s], "config_version", "site", s, [str], "str")
    if sites[s]["config_version"] not in version_dict:
      raise DataIntegrityError(
        f"Site {s} is version {sites[s]['config_version']}, which is currently not supported. Latest supported version is {site_latest_version}"
      )
    version_old = sites[s]["config_version"]

    # Update routines for old versions
    if version_dict[sites[s]
                    ["config_version"]] < version_dict[site_latest_version]:
      # Update routines for config_version 0.1.0
      if sites[s]["config_version"] == "0.1.0":
        sites[s]["config_version"] = "0.1.1"
      # Update routines for config_version 0.1.1
      if sites[s]["config_version"] == "0.1.1":
        sites[s]["dns"] = ["1.1.1.1", "8.8.8.8"]
        sites[s]["config_version"] = "0.1.2"
      # Update routines for config_version 0.1.2
      if sites[s]["config_version"] == "0.1.2":
        sites[s]["config_version"] = "0.1.3"

    # Newer version -> Error
    elif version_dict[sites[s]
                      ["config_version"]] > version_dict[site_latest_version]:
      raise DataIntegrityError(
        f"Site {s} is version {sites[s]['config_version']}, which is currently not supported. Latest supported version is {site_latest_version}"
      )

    # Data integrity check

    # Check ip_networks
    __check_key(sites[s], "ip_networks", "site", s, [list], "list")
    for n in sites[s]["ip_networks"]:
      __check_datatype(n, "key", "ip_networks", [str], "str")
    try:
      allow_ipv4, allow_ipv6 = check_ip_networks(sites[s]["ip_networks"])
    except IPNetworkError as e:
      raise IPNetworkError(f"Site: {s} - Key: \"ip_networks\"\n" + str(e))

    # Check DNS servers
    __check_key(sites[s], "dns", "site", s, [list], "list")
    for d in sites[s]["dns"]:
      __check_datatype(d, "key", "dns", [str], "str")
    try:
      check_dns(dns=sites[s]["dns"],
                allow_ipv4=allow_ipv4,
                allow_ipv6=allow_ipv6)
    except DNSError as e:
      raise DNSError(f"Site: {s} - Key: \"dns\"\n" + str(e))

    # Check peers
    sites[s]["peers"] = check_peer_integrity(Peers(sites[s]["peers"]), s,
                                             allow_ipv4, allow_ipv6,
                                             version_old)

  return sites


def check_peer_integrity(peers: Peers, site_name: str, allow_ipv4: bool,
                         allow_ipv6: bool, version_old: str) -> Peers:
  for p in peers:
    # Update routines for old versions
    if version_dict[version_old] < version_dict[site_latest_version]:
      # Update routines for config_version 0.1.0
      version = version_old
      if version == "0.1.0":
        peers[p]["post_up"] = ""
        peers[p]["post_down"] = ""
        peers[p]["ipv6_routing_fix"] = False

        __check_key(peers[p], "redirect_all_traffic", "peer",
                    f"{p} (site \"{site_name}\")", [bool, None],
                    "bool or null")
        if peers[p]["redirect_all_traffic"] == True:
          peers[p]["redirect_all_traffic"] = RedirectAllTraffic({
            "ipv4": True,
            "ipv6": True
          })
        elif peers[p]["redirect_all_traffic"] == False:
          peers[p]["redirect_all_traffic"] = RedirectAllTraffic({
            "ipv4": False,
            "ipv6": False
          })
        version = "0.1.1"
      if version == "0.1.1":
        peers[p]["dns"] = ["1.1.1.1", "8.8.8.8"]
        version = "0.1.2"
      if version == "0.1.2":
        if peers[p]["redirect_all_traffic"] == None:
          peers[p]["redirect_all_traffic"] = RedirectAllTraffic({
            "ipv4": False,
            "ipv6": False
          })
        version = "0.1.3"

    # Data integrity check

    # Check keys
    __check_key(peers[p], "keys", "peer", f"{p} (site \"{site_name}\")",
                [dict], "dict")
    for k in peers[p]["keys"]:
      __check_key(peers[p]["keys"], k, "keys", k, [str], "str")

    # Check additional allowed ips
    __check_key(peers[p], "additional_allowed_ips", "peer",
                f"{p} (site \"{site_name}\")", [list], "list")
    try:
      check_additional_allowed_ips(
        additional_allowed_ips=peers[p]["additional_allowed_ips"],
        allow_ipv4=allow_ipv4,
        allow_ipv6=allow_ipv6)
    except AdditionalAllowedIPError as e:
      raise AdditionalAllowedIPError(
        "Site: {site_name} - Peer {p} - Key: \"additional_allowed_ips\"\n" +
        str(e))

    # Check DNS servers
    __check_key(peers[p], "dns", "site", f"{p} (site \"{site_name}\")", [list],
                "list")
    for d in peers[p]["dns"]:
      __check_datatype(d, "key", "dns", [str], "str")
    try:
      check_dns(dns=peers[p]["dns"],
                allow_ipv4=allow_ipv4,
                allow_ipv6=allow_ipv6)
    except DNSError as e:
      raise DNSError(f"Site: {site_name} - Peer {p} - Key: \"dns\"\n" + str(e))

    # Check ingoing and outgoing_connected_peers and main_peer
    # If peer p2 is outgoing_connected_peer of peer p1, p1 has to be ingoing_connected of peer p2.
    __check_key(peers[p], "outgoing_connected_peers", "peer",
                f"{p} (site \"{site_name}\")", [list], "list")
    __check_key(peers[p], "main_peer", "peer", f"{p} (site \"{site_name}\")",
                [str], "str")
    __check_key(peers[p], "ingoing_connected_peers", "peer",
                f"{p} (site \"{site_name}\")", [list], "list")

    try:
      check_peer_connections(p, peers)
    except PeerConnectionError as e:
      raise PeerConnectionError(
        f"Site: {site_name} - Peer {p} - Peer connections\n" + str(e))

    # Check endpoint
    __check_key(peers[p], "endpoint", "peer", f"{p} (site \"{site_name}\")",
                [str], "str")
    check_endpoint(peers[p]["endpoint"], peers[p]["ingoing_connected_peers"])

    # Check port
    __check_key(peers[p], "port", "peer", f"{p} (site \"{site_name}\")", [int],
                "int")
    check_port(peers[p]["port"], peers[p]["ingoing_connected_peers"])

    # Check redirect_all_traffic
    __check_key(peers[p], "redirect_all_traffic", "peer",
                f"{p} (site \"{site_name}\")", [dict], "dict")
    if peers[p]["redirect_all_traffic"]:
      __check_key(
        peers[p]["redirect_all_traffic"], "ipv4", "key",
        f"ipv4 in \"redirect_all_traffic\" (peer {p} from site \"{site_name}\")",
        [bool], "bool")
      __check_key(
        peers[p]["redirect_all_traffic"], "ipv6", "key",
        f"ipv6 in \"redirect_all_traffic\" (peer {p} from site \"{site_name}\")",
        [bool], "bool")

    # Check post_up and post_down
    __check_key(peers[p], "post_up", "peer", f"{p} (site \"{site_name}\")",
                [str], "str")
    __check_key(peers[p], "post_down", "peer", f"{p} (site \"{site_name}\")",
                [str], "str")

    # Check ipv6_routing_fix
    __check_key(peers[p], "ipv6_routing_fix", "peer",
                f"{p} (site \"{site_name}\")", [bool], "bool")

  return peers


def check_imported_settings(settings: Settings) -> Settings:
  # Update routines for old file versions
  __check_key(settings, "file_version", "key", "settings", [str], "str")
  if settings["file_version"] not in version_dict:
    raise DataIntegrityError(
      f"The settings are version {settings['file_version']}, which is currently not supported. Latest supported version is {settings_latest_version}"
    )
  if version_dict[
      settings["file_version"]] < version_dict[settings_latest_version]:
    # Update routines for config_version 0.1.0
    if settings["file_version"] == "0.1.0":
      if os.name in ["nt", "dos"]:
        settings["wg_exec"] = "C:\\Program Files\\WireGuard\\wg.exe"
      else:
        settings["wg_exec"] = "wg"
      settings["file_version"] = "0.1.1"
  elif version_dict[
      settings["file_version"]] > version_dict[settings_latest_version]:
    raise DataIntegrityError(
      f"The settings are version {settings['file_version']}, which is currently not supported. Latest supported version is {settings_latest_version}"
    )

  # Data integrity check

  # Flags

  # Check keys
  __check_key(settings, "verbosity", "key", "settings", [int], "int")
  __check_key(settings, "sites_file_path", "key", "settings", [str], "str")
  __check_key(settings, "wg_config_path", "key", "settings", [str], "str")
  __check_key(settings, "editor", "key", "settings", [str], "str")

  return settings


def check_ip_networks(ip_networks: list) -> tuple[bool, bool]:
  allow_ipv4 = False
  allow_ipv6 = False
  for n in ip_networks:
    try:
      ip_network = ipaddress.ip_network(n)
    except ValueError:
      raise IPNetworkError(f"{n} is no valid IP-Network")

    version = ip_network.version
    if version == 4 and ip_network.prefixlen > 30:
      raise IPNetworkError(
        f"{n} has a prefix of {ip_network.prefixlen}, which is too high")
    elif version == 6 and ip_network.prefixlen > 126:
      raise IPNetworkError(
        f"{n} has a prefix of {ip_network.prefixlen}, which is too high")

    if version == 4:
      allow_ipv4 = True
    if version == 6:
      allow_ipv6 = True
  return allow_ipv4, allow_ipv6


def check_additional_allowed_ips(additional_allowed_ips: list,
                                 allow_ipv4: bool, allow_ipv6: bool):
  for a in additional_allowed_ips:
    try:
      v = ipaddress.ip_network(a).version
    except ValueError:
      raise AdditionalAllowedIPError(
        f"{a} is no valid IP network (e.g. 10.0.0.0/24 or fd01::/64)")
    if v == 4 and not allow_ipv4:
      raise AdditionalAllowedIPError(
        f"{a} is IPv4, but IPv4 is not activated in this site")
    elif v == 6 and not allow_ipv6:
      raise AdditionalAllowedIPError(
        f"{a} is IPv6, but IPv6 is not activated in this site")


def check_dns(dns: list, allow_ipv4, allow_ipv6):
  for d in dns:
    try:
      dns_ip_version = ipaddress.ip_address(d).version
    except ValueError:
      raise DNSError(f"{d} is not a valid IP address (e.g. 1.1.1.1)")
    if (not allow_ipv4 and dns_ip_version == 4) or (not allow_ipv6
                                                    and dns_ip_version == 6):
      raise DNSError(
        f"{d} is an IPv{dns_ip_version} address, but IPv{dns_ip_version} is not allowed"
      )


def check_peer_connections(peer_name: str, peers: Peers):
  # Check outgoing peers
  for outgoing_peer in peers[peer_name]["outgoing_connected_peers"]:
    # Check if outgoing_peer exists
    if outgoing_peer not in peers:
      raise PeerConnectionError(
        f"{outgoing_peer} is set as outgoing_peer, but does not exist at all")
    # Check if p is an ingoing_peer in outgoing_peer
    if peer_name not in peers[outgoing_peer]["ingoing_connected_peers"]:
      raise PeerConnectionError(
        f"{peer_name} is not set as ingoing_peer in {outgoing_peer}")

  # Check ingoing peers
  for ingoing_peer in peers[peer_name]["ingoing_connected_peers"]:
    # Check if ingoing_peer exists
    if ingoing_peer not in peers:
      raise PeerConnectionError(
        f"{ingoing_peer} is set as ingoing_peer, but does not exist at all")
    # Check if p is an outgoing_peer in ingoing_peer
    if peer_name not in peers[ingoing_peer]["outgoing_connected_peers"]:
      raise PeerConnectionError(
        f"{peer_name} is not set as outgoing_peer in {ingoing_peer}")

  # Check if main_peer is present and an outgoing_peer
  if peers[peer_name]["outgoing_connected_peers"] and (
      peers[peer_name]["main_peer"]
      not in peers[peer_name]["outgoing_connected_peers"]):
    raise PeerConnectionError(
      f"{peers[peer_name]['main_peer']} is not an outgoing_peer")


def check_endpoint(endpoint: str, ingoing_connected_peers: list):
  # If it is not an URL it has to be an IP address
  if ingoing_connected_peers and re.match(r"^(?:[a-zA-Z0-9]+[.])*[a-z]{2,12}$",
                                          endpoint) is None:
    try:
      ipaddress.ip_address(endpoint)
    except ValueError:
      raise EndpointError(
        f"{endpoint} is not a valid domain name (eg. \"example.com\") or IP address (e.g. 1.1.1.1)"
      )


def check_port(port: int, ingoing_connected_peers: list):
  if ingoing_connected_peers and (port < 1 or port > 65535):
    raise PortError(f"{port} is not a valid port number (range 1-65535)")


def __check_key(d: dict, key: str, what_is_checked: str, dict_name: str,
                datatypes: list, datatype_name: str):
  __check_key_presence(d, key, what_is_checked, dict_name, datatype_name)
  __check_datatype(d[key], what_is_checked, dict_name, datatypes,
                   datatype_name)


def __check_key_presence(d: dict, key: str, what_is_checked: str,
                         dict_name: str, datatype_name: str):
  try:
    d[key]
  except KeyError:
    raise DataIntegrityError(
      f"Key \"{key}\" not present in {what_is_checked} \"{dict_name}\"")


def __check_datatype(o, what_is_checked: str, dict_name: str, datatypes: list,
                     datatype_name: str):
  valid = False
  for d in datatypes:
    if d is None:
      if o is None:
        valid = True
    elif isinstance(o, d):
      valid = True
  if not valid:
    raise DataIntegrityError(
      f"\"{o}\" in {what_is_checked} \"{dict_name}\" should be {datatypes} not {type(o)}"
    )
