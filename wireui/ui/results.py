from ..library import AAIPs_MESSAGE_TYPE
from ..library import DNS_MESSAGE_TYPE
from ..library import ENDPOINT_MESSAGE_TYPE
from ..library import IP_NETWORK_MESSAGE_TYPE
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
from ..library import Message
from ..library import PortMessage
from ..library import PortMessageContent
from ..library import Result
from ..library import ResultList


def get_result_list_messages(rl: ResultList):
  s = ""
  for r in rl:
    s += get_result_message(r)
  return s


def get_result_message(r: Result) -> str:
  s = ""
  for m in r:
    if isinstance(m.get_message(), DNSMessageContent):
      s += __get_dns_message(m)
    elif isinstance(m.get_message(), IPNetworkMessageContent):
      s += __get_ip_network_message(m)
    elif isinstance(m.get_message(), EndpointMessageContent):
      s += __get_endpoint_message(m)
    elif isinstance(m.get_message(), PortMessageContent):
      s += __get_port_message(m)
    elif isinstance(m.get_message(), AAIPsMessageContent):
      s += __get_aaips_message(m)
  return s


def __get_dns_message(msg: DNSMessage) -> str:
  s = ""
  if msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_INVALID:
    s += __get_message_level(msg)
    s += f"{msg.get_message().ip_address} is not a valid IP address\n"
  elif msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION:
    s += __get_message_level(msg)
    s += f"{msg.get_message().ip_address} has a wrong IP address version\n"
  return s


def __get_ip_network_message(msg: IPNetworkMessage) -> str:
  s = ""
  if msg.get_message(
  ).message_type == IP_NETWORK_MESSAGE_TYPE.IP_NETWORK_INVALID:
    s += __get_message_level(msg)
    s += f"{msg.get_message().ip_network} is not a valid IP network\n"
  elif msg.get_message().message_type == DNS_MESSAGE_TYPE.IP_ADDRESS_VERSION:
    s += __get_message_level(msg)
    s += f"{msg.get_message().ip_network} has a too high prefix. Prefix is {msg.get_message().prefix}.\n"
  return s


def __get_endpoint_message(msg: EndpointMessage) -> str:
  s = ""
  if msg.get_message().message_type == ENDPOINT_MESSAGE_TYPE.ENDPOINT_INVALID:
    s += __get_message_level(msg)
    s += f"{msg.get_message().endpoint} is not a valid URL or IP address\n"
  return s


def __get_port_message(msg: PortMessage) -> str:
  s = ""
  if msg.get_message().message_type == PORT_MESSAGE_TYPE.PORT_INVALID:
    s += __get_message_level(msg)
    s += f"{msg.get_message().port} is of range. Port must be within 1-65535\n"
  return s


def __get_aaips_message(msg: AAIPsMessage) -> str:
  s = ""
  if msg.get_message().message_type == AAIPs_MESSAGE_TYPE.IP_NETWORK_INVALID:
    s += __get_message_level(msg)
    s += f"{msg.get_message().ip_network} is not a valid IP network.\n"
  elif msg.get_message().message_type == AAIPs_MESSAGE_TYPE.IPv4_NOT_ACTIVATED:
    s += __get_message_level(msg)
    s += f"{msg.get_message().ip_network} is IPv4, but IPv4 is not allowed.\n"
  elif msg.get_message().message_type == AAIPs_MESSAGE_TYPE.IPv6_NOT_ACTIVATED:
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
