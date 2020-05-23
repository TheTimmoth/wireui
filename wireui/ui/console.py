# console.py
# Write text and error messages to console
# Author: Tim Schlottmann

import sys

_verbosity = 2


def set_verbosity(verbosity: int = 0):
  """Sets the verbosity level of the console output"""

  assert isinstance(
      verbosity, int
  ), f"verbosity should be <class \'int\'> and not {str(type(verbosity))}"
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
