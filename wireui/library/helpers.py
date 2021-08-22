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
