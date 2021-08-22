import os


def vline() -> str:
  columns, _ = os.get_terminal_size()
  s = ""
  s = s.join(["-" for _ in range(columns)])
  return s
