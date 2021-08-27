from typing import Optional

from ..library import AAIPs_MESSAGE_TYPE
from ..library import DNS_MESSAGE_TYPE
from ..library import ENDPOINT_MESSAGE_TYPE
from ..library import IP_NETWORK_MESSAGE_TYPE
from ..library import KEY_DATATYPE_MESSAGE_TYPE
from ..library import KEY_PRESENCE_MESSAGE_TYPE
from ..library import MESSAGE_LEVEL
from ..library import PORT_MESSAGE_TYPE
from ..library import AAIPsMessage
from ..library import AAIPsMessageContent
from ..library import DNSMessage
from ..library import DNSMessageContent
from ..library import EndpointMessage
from ..library import EndpointMessageContent
from ..library import IPNetworkMessage
from ..library import IPNetworkMessageContent
from ..library import KeyDatatypeMessage
from ..library import KeyDatatypeMessageContent
from ..library import KeyPresenceMessage
from ..library import KeyPresenceMessageContent
from ..library import Message
from ..library import PortMessage
from ..library import PortMessageContent
from ..library import Result
from ..library import ResultList

from ..shared import strings


def get_result_list_messages(rl: ResultList, start: Optional[str] = ""):
  s = ""
  for r in rl:
    s += get_result_message(r, start)
  return s


def get_result_message(r: Result, start: Optional[str] = "") -> str:
  s = ""
  for m in r:
    t = start
    if isinstance(m.get_message(), DNSMessageContent):
      t += __get_dns_message(m)
    elif isinstance(m.get_message(), IPNetworkMessageContent):
      t += __get_ip_network_message(m)
    elif isinstance(m.get_message(), EndpointMessageContent):
      t += __get_endpoint_message(m)
    elif isinstance(m.get_message(), PortMessageContent):
      t += __get_port_message(m)
    elif isinstance(m.get_message(), AAIPsMessageContent):
      t += __get_aaips_message(m)
    elif isinstance(m.get_message(), KeyPresenceMessageContent):
      t += __get_key_presence_message(m)
    elif isinstance(m.get_message(), KeyDatatypeMessageContent):
      t += __get_key_datatype_message(m)
    if t == start:
      t = ""
    s += t
  return s


def __get_dns_message(msg: DNSMessage) -> str:
  s = ""
  if msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_INVALID:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['dns_invalid']}\n".format(
      msg.get_message().ip_address)
  elif msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['dns_ip_version_wrong']}\n".format(
      msg.get_message().ip_address)
  return s


def __get_ip_network_message(msg: IPNetworkMessage) -> str:
  s = ""
  if msg.get_message(
  ).message_type == IP_NETWORK_MESSAGE_TYPE.IP_NETWORK_INVALID:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['ip_network_invalid']}\n".format(
      msg.get_message().ip_network)
  elif msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['ip_network_prefix']}\n".format(
      msg.get_message().ip_network,
      msg.get_message().prefix)
  return s


def __get_endpoint_message(msg: EndpointMessage) -> str:
  s = ""
  if msg.get_message().message_type == ENDPOINT_MESSAGE_TYPE.ENDPOINT_INVALID:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['endpoint_invalid']}\n".format(
      msg.get_message().endpoint)
  return s


def __get_port_message(msg: PortMessage) -> str:
  s = ""
  if msg.get_message().message_type == PORT_MESSAGE_TYPE.PORT_INVALID:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['port_invalid']}\n".format(
      msg.get_message().port)
  return s


def __get_aaips_message(msg: AAIPsMessage) -> str:
  s = ""
  if msg.get_message().message_type == AAIPs_MESSAGE_TYPE.IP_NETWORK_INVALID:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['aaips_network_invalid']}\n".format(
      msg.get_message().ip_network)
  elif msg.get_message().message_type == AAIPs_MESSAGE_TYPE.IPv4_NOT_ACTIVATED:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['aaips_ipv4_not_allowed']}\n".format(
      msg.get_message().ip_network)
  elif msg.get_message().message_type == AAIPs_MESSAGE_TYPE.IPv6_NOT_ACTIVATED:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['aaips_ipv6_not_allowed']}\n".format(
      msg.get_message().ip_network)
  return s


def __get_key_presence_message(msg: KeyPresenceMessage) -> str:
  s = ""
  if msg.get_message().message_type == KEY_PRESENCE_MESSAGE_TYPE.NOT_FOUND:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['key_presence_not_found']}\n".format(
      msg.get_message().key)
  return s


def __get_key_datatype_message(msg: KeyDatatypeMessage) -> str:
  s = ""
  if msg.get_message(
  ).message_type == KEY_DATATYPE_MESSAGE_TYPE.DATATYPE_WRONG:
    s += __get_message_level(msg)
    s += f"{strings['integrity']['key_datatype_wrong']}\n".format(
      msg.get_message().key,
      msg.get_message().datatype_actual,
      msg.get_message().datatypes_target)
  return s


def __get_message_level(msg: Message) -> str:
  s = ""
  if msg.get_message_level() == MESSAGE_LEVEL.ERROR:
    s += f"[{strings['misc']['error']}] "
  elif msg.get_message_level() == MESSAGE_LEVEL.WARNING:
    s += f"[{strings['misc']['warning']}] "
  elif msg.get_message_level() == MESSAGE_LEVEL.INFORMATION:
    s += f"[{strings['misc']['information']}] "
  return s
