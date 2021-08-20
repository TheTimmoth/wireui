import os

author = "Tim Schlottmann"
copyright = "(C) 2020-2021"
description = "Tool for creating and managing wireguard configs"
name = "WireUI"
version = "0.1.0a"


def get_vline() -> str:
  columns, _ = os.get_terminal_size()
  s = ""
  s = s.join(["-" for _ in range(columns)])
  return s
