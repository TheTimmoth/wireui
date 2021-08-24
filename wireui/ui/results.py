from ..library import AAIPs_MESSAGE_TYPE
from ..library import DNS_MESSAGE_TYPE
from ..library import ENDPOINT_MESSAGE_TYPE
from ..library import IP_NETWORK_MESSAGE_TYPE
from ..library import MESSAGE_LEVEL
from ..library import PORT_MESSAGE_TYPE
from ..library import AAIPsResult
from ..library import DNSResult
from ..library import EndpointResult
from ..library import IPNetworkResult
from ..library import PortResult
from ..library import Message


def check_dns_result(r: DNSResult) -> str:
  s = ""
  if r:
    for msg in r:
      if msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_INVALID:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_address} is not a valid IP address\n"
      elif msg.get_message(
      ).message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_address} has a wrong IP address version\n"
  return s


def check_ip_network_result(r: IPNetworkResult) -> str:
  s = ""
  if r:
    for msg in r:
      if msg.get_message(
      ).message_type == IP_NETWORK_MESSAGE_TYPE.IP_NETWORK_INVALID:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_network} is not a valid IP network\n"
      elif msg.get_message(
      ).message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_network} has a too high prefix. Prefix is {msg.get_message().prefix}.\n"
  return s


def check_endpoint_result(r: EndpointResult) -> str:
  s = ""
  if r:
    for msg in r:
      if msg.get_message(
      ).message_type == ENDPOINT_MESSAGE_TYPE.ENDPOINT_INVALID:
        s += __get_message_level(msg)
        s += f"{msg.get_message().endpoint} is not a valid URL or IP address\n"
  return s


def check_port_result(r: PortResult) -> str:
  s = ""
  if r:
    for msg in r:
      if msg.get_message().message_type == PORT_MESSAGE_TYPE.PORT_INVALID:
        s += __get_message_level(msg)
        s += f"{msg.get_message().port} is of range. Port must be within 1-65535\n"
  return s


def check_aaips_result(r: AAIPsResult) -> str:
  s = ""
  if r:
    for msg in r:
      if msg.get_message(
      ).message_type == AAIPs_MESSAGE_TYPE.IP_NETWORK_INVALID:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_network} is not a valid IP network.\n"
      elif msg.get_message(
      ).message_type == AAIPs_MESSAGE_TYPE.IPv4_NOT_ACTIVATED:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_network} is IPv4, but IPv4 is not allowed.\n"
      elif msg.get_message(
      ).message_type == AAIPs_MESSAGE_TYPE.IPv6_NOT_ACTIVATED:
        s += __get_message_level(msg)
        s += f"{msg.get_message().ip_network} is IPv6, but IPv6 is not allowed.\n"
  return s


def __get_message_level(msg: Message) -> str:
  s = ""
  if msg.get_message_level() == MESSAGE_LEVEL.ERROR:
    s += "[Error] "
  elif msg.get_message_level() == MESSAGE_LEVEL.WARNING:
    s += "[Warning] "
  elif msg.get_message_level() == MESSAGE_LEVEL.INFORMATION:
    s += "[Information] "
  return s
