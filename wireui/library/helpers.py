from typing import List


def convert_str_to_list(s: str) -> list:
  """ Convert a str to a list.

  Doubled entires are removed and the list is sorted. """

  l = list(set(s.split()))
  l.sort()
  return l


def convert_list_to_str(l: list) -> str:
  """ Convert a list to a str.

  Elements are separated with ' '"""

  s = ""
  for e in l:
    s += f"{e} "

  return s[:-1]


def get_default_dns(allow_ipv4: bool, allow_ipv6: bool) -> List[str]:
  default_dns = []
  if allow_ipv4:
    default_dns.append("1.1.1.1")
  if allow_ipv6:
    default_dns.append("2606:4700:4700::1111")
  return default_dns
