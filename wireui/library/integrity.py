# integrity.py
# Check program and data integrity
# Author: Tim Schlottmann

import ipaddress
from .typedefs.exceptions import WireguardNotFoundError

from .keys import get_keys
from .typedefs import DataIntegrityError
from .typedefs import PeerItems
from .typedefs import Peers
from .typedefs import RedirectAllTraffic
from .typedefs import Settings
from .typedefs import SiteItems
from .typedefs import Sites

version_dict = {
  "0.1.0": 1,
  "0.1.1": 2,
  "0.1.2": 3,
}

settings_latest_version = "0.1.0"
site_latest_version = "0.1.2"


def check_wireguard():
  get_keys()


# Data check recipe
#
# A check is done after the following recipe:
# 1. Check if a key is present
# 2. Check if the value has the correct datatype
# 3. If the value is of type list or dict repeat step 2
# 4. Make additional checks where applicable


def check_site_integrity(sites: Sites) -> Sites:
  """ Check data integrity of the sites """
  for s in sites:
    # Check config_version
    _check_key(sites[s], "config_version", "site", s, [str], "str")
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

    # Newer version -> Error
    elif version_dict[sites[s]
                      ["config_version"]] > version_dict[site_latest_version]:
      raise DataIntegrityError(
        f"Site {s} is version {sites[s]['config_version']}, which is currently not supported. Latest supported version is {site_latest_version}"
      )

    # Data integrity check

    #Flags
    ipv4_network = False
    ipv6_network = False

    # Check ip_networks
    _check_key(sites[s], "ip_networks", "site", s, [list], "list")
    for n in sites[s]["ip_networks"]:
      _check_datatype(n, "key", "ip_networks", [str], "str")
      try:
        v = ipaddress.ip_network(n).version
      except Exception as e:
        raise DataIntegrityError(
          f"{n} in key \"ip_networks\" in site {s} is not a valid IP network\n{e}"
        )
      if v == 4:
        ipv4_network = True
      elif v == 6:
        ipv6_network = True

    # Check DNS servers
    _check_key(sites[s], "dns", "site", s, [list], "list")
    for d in sites[s]["dns"]:
      _check_datatype(d, "key", "dns", [str], "str")
      try:
        v = ipaddress.ip_address(d)
      except ValueError as e:
        raise DataIntegrityError(
          f"{d} in key \"dns\" in site {s} is not a valid IP address\n{e}")

    # Check peers
    sites[s]["peers"] = check_peer_integrity(Peers(sites[s]["peers"]), s,
                                             ipv4_network, ipv6_network,
                                             version_old)

  return sites


def check_peer_integrity(peers: Peers, site_name: str, ipv4_network: bool,
                         ipv6_network: bool, version_old: str) -> Peers:
  for p in peers:
    # Update routines for old versions
    if version_dict[version_old] < version_dict[site_latest_version]:
      # Update routines for config_version 0.1.0
      version = version_old
      if version == "0.1.0":
        peers[p]["post_up"] = ""
        peers[p]["post_down"] = ""
        peers[p]["ipv6_routing_fix"] = False

        _check_key(peers[p], "redirect_all_traffic", "peer",
                   f"{p} (site \"{site_name}\")", [bool, None], "bool or null")
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

    # Flags

    # Check keys
    _check_key(peers[p], "keys", "peer", f"{p} (site \"{site_name}\")", [dict],
               "dict")
    for k in peers[p]["keys"]:
      _check_key(peers[p]["keys"], k, "keys", k, [str], "str")

    # Check additional allowed ips
    _check_key(peers[p], "additional_allowed_ips", "peer",
               f"{p} (site \"{site_name}\")", [list], "list")
    for n in peers[p]["additional_allowed_ips"]:
      try:
        v = ipaddress.ip_network(n).version
      except Exception as e:
        raise DataIntegrityError(
          f"{n} in key \"additional_allowed_ips\" in peer {p} (site \"{site_name}\") is not a valid IP network\n{e}"
        )
      if v == 4 and not ipv4_network:
        raise DataIntegrityError(
          f"{n} in key \"additional_allowed_ips\" in peer {p} (site \"{site_name}\") is IPv4, but IPv4 is not activated in the site"
        )
      elif v == 6 and not ipv6_network:
        raise DataIntegrityError(
          f"{n} in key \"additional_allowed_ips\" in peer {p} (site \"{site_name}\") is IPv6, but IPv6 is not activated in the site"
        )

    # Check DNS servers
    _check_key(peers[p], "dns", "site", f"{p} (site \"{site_name}\")", [list],
               "list")
    for d in peers[p]["dns"]:
      _check_datatype(d, "key", "dns", [str], "str")
      try:
        v = ipaddress.ip_address(d)
      except ValueError as e:
        raise DataIntegrityError(
          f"{d} in key \"dns\" in peer {p} is not a valid IP address\n{e}")

    # Check ingoing and outgoing_connected_peers and main_peer
    # If peer p2 is outgoing_connected_peer of peer p1, p1 has to be ingoing_connected of peer p2.
    _check_key(peers[p], "outgoing_connected_peers", "peer",
               f"{p} (site \"{site_name}\")", [list], "list")
    _check_key(peers[p], "main_peer", "peer", f"{p} (site \"{site_name}\")",
               [str], "str")
    _check_key(peers[p], "ingoing_connected_peers", "peer",
               f"{p} (site \"{site_name}\")", [list], "list")

    for outgoing_peer in peers[p]["outgoing_connected_peers"]:
      if outgoing_peer not in peers:
        raise DataIntegrityError(
          f"{outgoing_peer} is set as outgoing peer in peer {p} (site \"{site_name}\"), but is not present in peers-list."
        )
      if p not in peers[outgoing_peer]["ingoing_connected_peers"]:
        raise DataIntegrityError(
          f"{outgoing_peer} is set as outgoing peer in peer {p} (site \"{site_name}\"), but is not present as ingoing_connected_peer in peer {outgoing_peer}"
        )
    for ingoing_peer in peers[p]["ingoing_connected_peers"]:
      if ingoing_peer not in peers:
        raise DataIntegrityError(
          f"{ingoing_peer} is set as ingoing peer in peer {p} (site \"{site_name}\"), but is not present in peers-list."
        )
      if p not in peers[ingoing_peer]["outgoing_connected_peers"]:
        raise DataIntegrityError(
          f"{ingoing_peer} is set as ingoing peer in peer {p} (site \"{site_name}\"), but is not present as ingoing_connected_peer in peer {ingoing_peer}"
        )
    if peers[p]["outgoing_connected_peers"] and (
        peers[p]["main_peer"] not in peers[p]["outgoing_connected_peers"]):
      raise DataIntegrityError(
        f"{peers[p]['main_peer']} in peer {p} (site \"{site_name}\") is mentioned as main_peer, but is not present as outgoing_connected_peer"
      )

    # Check endpoint
    _check_key(peers[p], "endpoint", "peer", f"{p} (site \"{site_name}\")",
               [str], "str")

    # Check port
    _check_key(peers[p], "port", "peer", f"{p} (site \"{site_name}\")", [int],
               "int")

    # Check redirect_all_traffic
    _check_key(peers[p], "redirect_all_traffic", "peer",
               f"{p} (site \"{site_name}\")", [dict, None], "dict or null")
    if peers[p]["redirect_all_traffic"]:
      _check_key(
        peers[p]["redirect_all_traffic"], "ipv4", "key",
        f"ipv4 in \"redirect_all_traffic\" (peer {p} from site \"{site_name}\")",
        [bool], "bool")
      _check_key(
        peers[p]["redirect_all_traffic"], "ipv6", "key",
        f"ipv6 in \"redirect_all_traffic\" (peer {p} from site \"{site_name}\")",
        [bool], "bool")

    # Check post_up and post_down
    _check_key(peers[p], "post_up", "peer", f"{p} (site \"{site_name}\")",
               [str], "str")
    _check_key(peers[p], "post_down", "peer", f"{p} (site \"{site_name}\")",
               [str], "str")

    # Check ipv6_routing_fix
    _check_key(peers[p], "ipv6_routing_fix", "peer",
               f"{p} (site \"{site_name}\")", [bool], "bool")

  return peers


def check_settings_integrity(settings: Settings) -> Settings:
  # Update routines for old file versions
  _check_key(settings, "file_version", "key", "settings", [str], "str")
  if settings["file_version"] not in version_dict:
    raise DataIntegrityError(
      f"The settings are version {settings['file_version']}, which is currently not supported. Latest supported version is {settings_latest_version}"
    )
  if version_dict[
      settings["file_version"]] < version_dict[settings_latest_version]:
    # Put update routines here
    pass
  elif version_dict[
      settings["file_version"]] > version_dict[settings_latest_version]:
    raise DataIntegrityError(
      f"The settings are version {settings['file_version']}, which is currently not supported. Latest supported version is {settings_latest_version}"
    )

  # Data integrity check

  # Flags

  # Check keys
  _check_key(settings, "verbosity", "key", "settings", [int], "int")
  _check_key(settings, "sites_file_path", "key", "settings", [str], "str")
  _check_key(settings, "wg_config_path", "key", "settings", [str], "str")
  _check_key(settings, "editor", "key", "settings", [str], "str")

  return settings


def _check_key(d: dict, key: str, what_is_checked: str, dict_name: str,
               datatypes: list, datatype_name: str):
  _check_key_presence(d, key, what_is_checked, dict_name, datatype_name)
  _check_datatype(d[key], what_is_checked, dict_name, datatypes, datatype_name)


def _check_key_presence(d: dict, key: str, what_is_checked: str,
                        dict_name: str, datatype_name: str):
  try:
    d[key]
  except KeyError:
    raise DataIntegrityError(
      f"Key \"{key}\" not present in {what_is_checked} \"{dict_name}\"")


def _check_datatype(o, what_is_checked: str, dict_name: str, datatypes: list,
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
