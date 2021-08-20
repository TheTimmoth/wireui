# console.py
# Write text and error messages to console
# Author: Tim Schlottmann

import os
import subprocess
import sys

from . import strings

_menu_list = []
_verbosity = 2


def set_verbosity(verbosity: int = 0):
  """Sets the verbosity level of the console output"""

  global _verbosity

  assert isinstance(
    verbosity,
    int), f"verbosity should be <class \'int\'> and not {str(type(verbosity))}"
  assert verbosity >= 0, f"verbosity should be >= 0 and not {verbosity}"
  _verbosity = verbosity


def print_message(verbosity: int, *args, **kwargs):
  """Prints a message to STDOUT

  The message is only printed, if verbosity is greater than the setted verbosity
  """

  if verbosity <= _verbosity:
    print(*args, file=sys.stdout, **kwargs)


def print_error(verbosity: int, *args, **kwargs):
  """Prints a message to STDERR

  The message is only printed, if verbosity is greater than the setted verbosity
  """

  if verbosity <= _verbosity:
    print(*args, file=sys.stderr, **kwargs)


def print_list(l: list):
  for e in l:
    print_message(0, e, end="     ")
  print_message(0, "", end="\n")


def yes_no_menu(string) -> bool:
  valid = False
  while not valid:
    choice = input(string + " [y/n] ")
    if choice == "y":
      choice = True
      valid = True
    elif choice == "n":
      choice = False
      valid = True
  return choice


def clear_screen():
  if os.name in ("nt", "dos"):
    os.system("cls")
  else:
    subprocess.run("clear")


def leave_menu():
  _menu_list.pop()


def write_header(name: str = ""):
  clear_screen()

  print_message(0, f"{strings.name} - {strings.version}")
  print_message(0, strings.get_vline())

  # It is assumed that all later menus are closed if name is already in list
  if name in _menu_list:
    while _menu_list.pop() != name:
      pass

  if name:
    _menu_list.append(name)

  s = ""
  for m in _menu_list:
    s += f"{m} --> "
  s = s[:-5]
  print_message(0, s)
  print_message(0, strings.get_vline())
