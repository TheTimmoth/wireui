# console.py
# Write text and error messages to console
# Author: Tim Schlottmann

import os
import subprocess
import sys

from typing import AnyStr
from typing import Dict
from typing import List
from typing import Optional

from .elements import vline

from ..shared import strings

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


def print_list(l: List[AnyStr]):
  for e in l:
    print_message(0, e, end="     ")
  print_message(0, "", end="\n")


def yes_no_menu(string: str, default: Optional[bool] = None) -> bool:
  valid = False
  while not valid:
    s = string + f" {strings['console']['yes_no_input']}".format(
      strings['misc']['yes_abbr'], strings['misc']['no_abbr'])
    if default != None:
      if default:
        default = f"{strings['misc']['yes_abbr']}"
      else:
        default = f"{strings['misc']['no_abbr']}"
      s += f"[{default}] "
    choice = input(s) or default
    if choice == strings['misc']['yes_abbr'] or choice == True:
      choice = True
      valid = True
    elif choice == strings['misc']['no_abbr'] or choice == False:
      choice = False
      valid = True
  return choice


def options_menu(options: Dict[str, str],
                 default: Optional[str] = None,
                 order: Optional[List[str]] = None) -> str:
  while True:
    print_header()
    print_message(0, f"{strings['console']['options_menu_header']}")
    if order:
      for k in order:
        print_message(0, f"{k}     {options[k]}")
    else:
      for k in options:
        print_message(0, f"{k}     {options[k]}")
    if default:
      choice = input(
        f"{strings['console']['options_menu_choose']} [{default}] ") or default
    else:
      choice = input(f"{strings['console']['options_menu_choose']} ")
    if choice in options:
      return choice


def clear_screen():
  if os.name in ("nt", "dos"):
    os.system("cls")
  else:
    subprocess.run("clear")


def leave_menu():
  __menu_list.pop()


def print_header(name: str = ""):
  clear_screen()

  print_message(
    0,
    f"{strings['app_information']['name']} - {strings['app_information']['version']}"
  )
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
