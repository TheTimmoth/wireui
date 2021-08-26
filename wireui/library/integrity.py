# integrity.py
# Check program existence and integrity from imported data
# Author: Tim Schlottmann

import os
import re
import ipaddress
from typing import List
from typing import NamedTuple
from typing import Optional

from .helpers import convert_list_to_str
from .helpers import get_default_dns

from .keys import get_keys

from .typedefs import MESSAGE_LEVEL
from .typedefs import DataIntegrityError
from .typedefs import DataIntegrityMessage
from .typedefs import DataIntegrityResult
from .typedefs import Message
from .typedefs import MessageContent
from .typedefs import Peers
from .typedefs import RedirectAllTraffic
from .typedefs import Result
from .typedefs import ResultList
from .typedefs import Settings
from .typedefs import Sites

version_dict = {
  "0.1.0": 1,
  "0.1.1": 2,
  "0.1.2": 3,
  "0.1.3": 4,
}

settings_latest_version = "0.1.2"
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

##########################################################################################
# Check imported site
##########################################################################################


def check_imported_sites(sites: Sites) -> DataIntegrityResult:
  """ Check data integrity of the sites """

  data_integrity_result = DataIntegrityResult()

  for s in sites:
    data_integrity_message = DataIntegrityMessage()
    site_result = ResultList(s)

    # Check config_version
    __check_key(sites[s], "config_version", "site", s, [str], "str")

    version_old = sites[s]["config_version"]

    # Newer version -> Error
    if sites[s]["config_version"] not in version_dict:
      raise DataIntegrityError(
        f"Site {s} is version {sites[s]['config_version']}, which is currently not supported. Latest supported version is {site_latest_version}"
      )

    # Update routines for old versions
    elif version_dict[sites[s]
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

    # Data integrity check

    # Check ip_networks
    __check_key(sites[s], "ip_networks", "site", s, [list], "list")
    for n in sites[s]["ip_networks"]:
      __check_datatype(n, "key", "ip_networks", [str], "str")
    r, allow_ipv4, allow_ipv6 = check_ip_networks(sites[s]["ip_networks"])
    site_result.append(r)

    # Check DNS servers
    __check_key(sites[s], "dns", "site", s, [list], "list")
    for d in sites[s]["dns"]:
      __check_datatype(d, "key", "dns", [str], "str")

    r = check_dns(dns=sites[s]["dns"],
                  allow_ipv4=allow_ipv4,
                  allow_ipv6=allow_ipv6)
    site_result.append(r)

    # Check peers
    peer_results = check_peer_integrity(Peers(sites[s]["peers"]), s,
                                        allow_ipv4, allow_ipv6, version_old)
    data_integrity_message.site_result = site_result
    data_integrity_message.peer_results = peer_results
    data_integrity_result.setitem(data_integrity_message)

  return data_integrity_result


def check_peer_integrity(peers: Peers, site_name: str, allow_ipv4: bool,
                         allow_ipv6: bool,
                         version_old: str) -> List[ResultList]:

  peer_results: List[ResultList] = []
  for p in peers:
    rl = ResultList(p)
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
    r = check_additional_allowed_ips(
      additional_allowed_ips=peers[p]["additional_allowed_ips"],
      allow_ipv4=allow_ipv4,
      allow_ipv6=allow_ipv6)
    rl.append(r)

    # Check DNS servers
    __check_key(peers[p], "dns", "site", f"{p} (site \"{site_name}\")", [list],
                "list")
    for d in peers[p]["dns"]:
      __check_datatype(d, "key", "dns", [str], "str")
    r = check_dns(dns=peers[p]["dns"],
                  allow_ipv4=allow_ipv4,
                  allow_ipv6=allow_ipv6)
    rl.append(r)

    # Check ingoing and outgoing_connected_peers and main_peer
    # If peer p2 is outgoing_connected_peer of peer p1, p1 has to be ingoing_connected of peer p2.
    __check_key(peers[p], "outgoing_connected_peers", "peer",
                f"{p} (site \"{site_name}\")", [list], "list")
    __check_key(peers[p], "main_peer", "peer", f"{p} (site \"{site_name}\")",
                [str], "str")
    __check_key(peers[p], "ingoing_connected_peers", "peer",
                f"{p} (site \"{site_name}\")", [list], "list")
    r = check_peer_connections(p, peers)
    rl.append(r)

    # Check endpoint
    __check_key(peers[p], "endpoint", "peer", f"{p} (site \"{site_name}\")",
                [str], "str")
    r = check_endpoint(peers[p]["endpoint"],
                       peers[p]["ingoing_connected_peers"])
    rl.append(r)

    # Check port
    __check_key(peers[p], "port", "peer", f"{p} (site \"{site_name}\")", [int],
                "int")
    r = check_port(peers[p]["port"], peers[p]["ingoing_connected_peers"])
    rl.append(r)

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

    peer_results.append(rl)

  return peer_results


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
    # Update routines for config_version 0.1.1
    if settings["file_version"] == "0.1.1":
      if os.name in ["nt", "dos"] and settings["editor"] == "editor":
        settings["editor"] = "C:\\Windows\\System32\\notepad.exe"
      settings["file_version"] = "0.1.2"
  elif version_dict[
      settings["file_version"]] > version_dict[settings_latest_version]:
    raise DataIntegrityError(
      f"The settings are version {settings['file_version']}, which is currently not supported. Latest supported version is {settings_latest_version}"
    )

  # Data integrity check

  # Check keys
  __check_key(settings, "verbosity", "key", "settings", [int], "int")
  __check_key(settings, "sites_file_path", "key", "settings", [str], "str")
  __check_key(settings, "wg_config_path", "key", "settings", [str], "str")
  __check_key(settings, "editor", "key", "settings", [str], "str")

  return settings


##########################################################################################
# Check IPNetworks
##########################################################################################


class IP_NETWORK_MESSAGE_TYPE():
  @property
  def IP_NETWORK_INVALID():
    return 0

  @property
  def PREFIX_TOO_HIGH():
    return 1

  @property
  def SET_DEFAULT():
    return 2


class IPNetworkMessageContent(MessageContent):
  message_type: int
  ip_network: str
  prefix: int


IPNetworkMessage = Message[IPNetworkMessageContent]


def check_ip_networks(
    ip_networks: List[str],
    default_ip_networks: Optional[List[str]] = []
) -> tuple[Result, bool, bool]:
  allow_ipv4 = False
  allow_ipv6 = False
  r = Result()
  for n in list(ip_networks):
    try:
      ip_network = ipaddress.ip_network(n)
    except ValueError:
      r.append(
        IPNetworkMessage(
          message_level=MESSAGE_LEVEL.ERROR,
          message=IPNetworkMessageContent(
            message_type=IP_NETWORK_MESSAGE_TYPE.IP_NETWORK_INVALID,
            ip_network=n,
            prefix=0)))
      ip_networks.remove(n)
    else:
      version = ip_network.version
      if version == 4 and ip_network.prefixlen > 30:
        r.append(
          IPNetworkMessage(
            message_level=MESSAGE_LEVEL.ERROR,
            message=IPNetworkMessageContent(
              message_type=IP_NETWORK_MESSAGE_TYPE.PREFIX_TOO_HIGH,
              ip_network=n,
              prefix=ip_network.prefixlen)))
        ip_networks.remove(n)
      elif version == 6 and ip_network.prefixlen > 126:
        r.append(
          IPNetworkMessage(
            message_level=MESSAGE_LEVEL.ERROR,
            message=IPNetworkMessageContent(
              message_type=IP_NETWORK_MESSAGE_TYPE.PREFIX_TOO_HIGH,
              ip_network=n,
              prefix=ip_network.prefixlen)))
        ip_networks.remove(n)

      if version == 4 and n in ip_networks:
        allow_ipv4 = True
      if version == 6 and n in ip_networks:
        allow_ipv6 = True
  if not ip_networks:
    ip_network = default_ip_networks
    r.append(
      IPNetworkMessage(message_level=MESSAGE_LEVEL.INFORMATION,
                       message=IPNetworkMessageContent(
                         message_type=IP_NETWORK_MESSAGE_TYPE.SET_DEFAULT,
                         ip_network=convert_list_to_str(default_ip_networks),
                         prefix=0)))
  return r, allow_ipv4, allow_ipv6


##########################################################################################
# Check AdditionalAllowedIPs
##########################################################################################


class AAIPs_MESSAGE_TYPE():
  @property
  def IP_NETWORK_INVALID():
    return 0

  @property
  def IPv4_NOT_ACTIVATED():
    return 1

  @property
  def IPv6_NOT_ACTIVATED():
    return 2

  @property
  def SET_DEFAULT():
    return 3


class AAIPsMessageContent(MessageContent):
  message_type: int
  ip_network: str


AAIPsMessage = Message[AAIPsMessageContent]


def check_additional_allowed_ips(
    additional_allowed_ips: List[str],
    allow_ipv4: bool,
    allow_ipv6: bool,
    default_additional_allowed_ips: Optional[List[str]] = []) -> Result:

  r = Result()
  for a in list(additional_allowed_ips):
    try:
      v = ipaddress.ip_network(a).version
    except ValueError:
      r.append(
        AAIPsMessage(
          MESSAGE_LEVEL.ERROR,
          AAIPsMessageContent(AAIPs_MESSAGE_TYPE.IP_NETWORK_INVALID,
                              ip_network=a)))
      additional_allowed_ips.remove(a)
    if v == 4 and not allow_ipv4:
      r.append(
        AAIPsMessage(
          MESSAGE_LEVEL.ERROR,
          AAIPsMessageContent(AAIPs_MESSAGE_TYPE.IPv4_NOT_ACTIVATED,
                              ip_network=a)))
      additional_allowed_ips.remove(a)
    elif v == 6 and not allow_ipv6:
      r.append(
        AAIPsMessage(
          MESSAGE_LEVEL.ERROR,
          AAIPsMessageContent(AAIPs_MESSAGE_TYPE.IPv6_NOT_ACTIVATED,
                              ip_network=a)))
      additional_allowed_ips.remove(a)
  if not additional_allowed_ips:
    additional_allowed_ips = default_additional_allowed_ips
    r.append(
      AAIPsMessage(
        MESSAGE_LEVEL.INFORMATION,
        AAIPsMessageContent(AAIPs_MESSAGE_TYPE.SET_DEFAULT,
                            ip_network=additional_allowed_ips)))

  return r


##########################################################################################
# Check DNS
##########################################################################################


class DNS_MESSAGE_TYPE():
  @property
  def IP_ADDRESS_INVALID():
    return 0

  @property
  def IP_ADDRESS_VERSION():
    return 1

  @property
  def SET_DEFAULT():
    return 2


class DNSMessageContent(MessageContent):
  message_type: int
  ip_address: str


DNSMessage = Message[DNSMessageContent]


def check_dns(dns: List[str],
              allow_ipv4: bool,
              allow_ipv6: bool,
              default_dns: Optional[List[str]] = None) -> Result:
  r = Result()
  if default_dns == None:
    default_dns = get_default_dns(allow_ipv4=allow_ipv4, allow_ipv6=allow_ipv6)
  for d in list(dns):
    try:
      dns_ip_version = ipaddress.ip_address(d).version
    except ValueError:
      r.append(
        DNSMessage(message_level=MESSAGE_LEVEL.ERROR,
                   message=DNSMessageContent(
                     message_type=DNS_MESSAGE_TYPE.IP_ADDRESS_INVALID,
                     ip_address=d)))
      dns.remove(d)
    else:
      if (not allow_ipv4 and dns_ip_version == 4) or (not allow_ipv6
                                                      and dns_ip_version == 6):
        r.append(
          DNSMessage(message_level=MESSAGE_LEVEL.ERROR,
                     message=DNSMessageContent(
                       message_type=DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION,
                       ip_address=d)))
        dns.remove(d)
  if not dns:
    dns = default_dns
    r.append(
      DNSMessage(message_level=MESSAGE_LEVEL.INFORMATION,
                 message=DNSMessageContent(
                   message_type=DNS_MESSAGE_TYPE.SET_DEFAULT,
                   ip_address=convert_list_to_str(default_dns))))
  return r


##########################################################################################
# Check PeerConnections
##########################################################################################


class PEER_CONNECTIONS_MESSAGE_TYPE():
  @property
  def OUTGOING_PEER_NON_EXISTENCE():
    return 0

  @property
  def INGOING_PEER_NON_EXISTENCE():
    return 1

  @property
  def OUTGOING_PEER_NOT_INGOING():
    return 2

  @property
  def INGOING_PEER_NOT_OUTGOING():
    return 3

  @property
  def MAIN_PEER_NOT_OUTGOING():
    return 4

  @property
  def SET_DEFAULT():
    return 5


class PeerConnectionsMessageContent(MessageContent):
  message_type: int
  peer_1: str
  peer_2: str


PeerConnectionsMessage = Message[PeerConnectionsMessageContent]


def check_peer_connections(peer_name: str, peers: Peers) -> Result:
  r = Result()

  # Check outgoing peers
  for outgoing_peer in peers[peer_name]["outgoing_connected_peers"]:
    # Check if outgoing_peer exists
    if outgoing_peer not in peers:
      r.append(
        PeerConnectionsMessage(message_level=MESSAGE_LEVEL.ERROR,
                               message=PeerConnectionsMessageContent(
                                 message_type=PEER_CONNECTIONS_MESSAGE_TYPE.
                                 OUTGOING_PEER_NON_EXISTENCE,
                                 peer_1=peer_name,
                                 peer_2=outgoing_peer)))
    # Check if p is an ingoing_peer in outgoing_peer
    if peer_name not in peers[outgoing_peer]["ingoing_connected_peers"]:
      r.append(
        PeerConnectionsMessage(message_level=MESSAGE_LEVEL.ERROR,
                               message=PeerConnectionsMessageContent(
                                 message_type=PEER_CONNECTIONS_MESSAGE_TYPE.
                                 OUTGOING_PEER_NOT_INGOING,
                                 peer_1=peer_name,
                                 peer_2=outgoing_peer)))

  # Check ingoing peers
  for ingoing_peer in peers[peer_name]["ingoing_connected_peers"]:
    # Check if ingoing_peer exists
    if ingoing_peer not in peers:
      r.append(
        PeerConnectionsMessage(message_level=MESSAGE_LEVEL.ERROR,
                               message=PeerConnectionsMessageContent(
                                 message_type=PEER_CONNECTIONS_MESSAGE_TYPE.
                                 INGOING_PEER_NON_EXISTENCE,
                                 peer_1=peer_name,
                                 peer_2=ingoing_peer)))
    # Check if p is an outgoing_peer in ingoing_peer
    if peer_name not in peers[ingoing_peer]["outgoing_connected_peers"]:
      r.append(
        PeerConnectionsMessage(message_level=MESSAGE_LEVEL.ERROR,
                               message=PeerConnectionsMessageContent(
                                 message_type=PEER_CONNECTIONS_MESSAGE_TYPE.
                                 INGOING_PEER_NOT_OUTGOING,
                                 peer_1=peer_name,
                                 peer_2=ingoing_peer)))

  # Check if main_peer is present and an outgoing_peer
  if peers[peer_name]["outgoing_connected_peers"] and (
      peers[peer_name]["main_peer"]
      not in peers[peer_name]["outgoing_connected_peers"]):
    r.append(
      PeerConnectionsMessage(
        message_level=MESSAGE_LEVEL.ERROR,
        message=PeerConnectionsMessageContent(
          message_type=PEER_CONNECTIONS_MESSAGE_TYPE.MAIN_PEER_NOT_OUTGOING,
          peer_1=peer_name,
          peer_2="")))
  return r


##########################################################################################
# Check Endpoint
##########################################################################################


class ENDPOINT_MESSAGE_TYPE():
  @property
  def ENDPOINT_INVALID():
    return 0

  @property
  def SET_DEFAULT():
    return 1


class EndpointMessageContent(MessageContent):
  message_type: int
  endpoint: str


EndpointMessage = Message[EndpointMessageContent]


def check_endpoint(endpoint: str,
                   ingoing_connected_peers: list,
                   default_endpoint: Optional[str] = "") -> Result:
  r = Result()

  # If it is not an URL it has to be an IP address
  if ingoing_connected_peers and re.match(r"^(?:[a-zA-Z0-9]+[.])*[a-z]{2,12}$",
                                          endpoint) is None:
    try:
      ipaddress.ip_address(endpoint)
    except ValueError:
      r.append(
        EndpointMessage(message_level=MESSAGE_LEVEL.ERROR,
                        message=EndpointMessageContent(
                          message_type=ENDPOINT_MESSAGE_TYPE.ENDPOINT_INVALID,
                          endpoint=endpoint)))
      endpoint = ""
  if not endpoint:
    endpoint = default_endpoint
    r.append(
      EndpointMessage(message_level=MESSAGE_LEVEL.INFORMATION,
                      message=EndpointMessageContent(
                        message_type=ENDPOINT_MESSAGE_TYPE.SET_DEFAULT,
                        endpoint=endpoint)))
  return r


##########################################################################################
# Check Port
##########################################################################################


class __PortMessageType(NamedTuple):
  PORT_INVALID: int
  SET_DEFAULT: int


class PORT_MESSAGE_TYPE():
  @property
  def PORT_INVALID():
    return 0

  @property
  def SET_DEFAULT():
    return 1


class PortMessageContent(MessageContent):
  message_type: int
  port: int


PortMessage = Message[PortMessageContent]


def check_port(port: int,
               ingoing_connected_peers: list,
               default_port: Optional[int] = 51820) -> Result:
  r = Result()
  if ingoing_connected_peers and (port < 1 or port > 65535):
    r.append(
      PortMessage(message_level=MESSAGE_LEVEL.ERROR,
                  message=PortMessageContent(
                    message_type=PORT_MESSAGE_TYPE.PORT_INVALID, port=port)))
  return r


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
