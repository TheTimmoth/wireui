# console.py
# Write text and error messages to console
# Author: Tim Schlottmann

import os
import subprocess
import sys

from .elements import vline
from ..library import strings

__menu_list = []
__verbosity = 2


def set_verbosity(verbosity: int = 0):
  """Sets the verbosity level of the console output"""

  global __verbosity

  assert isinstance(
    verbosity,
    int), f"verbosity should be <class \'int\'> and not {str(type(verbosity))}"
  assert verbosity >= 0, f"verbosity should be >= 0 and not {verbosity}"
  __verbosity = verbosity


def print_message(verbosity: int, *args, **kwargs):
  """Prints a message to STDOUT

  The message is only printed, if verbosity is greater than the setted verbosity
  """

  if verbosity <= __verbosity:
    print(*args, file=sys.stdout, **kwargs)


def print_error(verbosity: int, *args, **kwargs):
  """Prints a message to STDERR

  The message is only printed, if verbosity is greater than the setted verbosity
  """

  if verbosity <= __verbosity:
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
  __menu_list.pop()


def write_header(name: str = ""):
  clear_screen()

  print_message(0, f"{strings.name} - {strings.version}")
  print_message(0, vline())

  # It is assumed that all later menus are closed if name is already in list
  if name in __menu_list:
    while __menu_list.pop() != name:
      pass

  if name:
    __menu_list.append(name)

  s = ""
  for m in __menu_list:
    s += f"{m} --> "
  s = s[:-5]
  print_message(0, s)
  print_message(0, vline())
