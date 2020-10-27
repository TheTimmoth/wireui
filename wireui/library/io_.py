import io
import json
import os
import subprocess
import tempfile

from .typedefs import ConnectionTable
from .typedefs import JsonDict
from .typedefs import JSONDecodeError


def write_file(path: str, s: str = "") -> str:
  """ Save a string to a file """
  with open(path, "w") as f:
    f.write(s)
    f.flush()
  return path


def read_file(path: str) -> str:
  """ Get the content of a file """
  try:
    with open(path, "r") as f:
      return f.read()
  except FileNotFoundError:
    return ""


# def write_jsonfile(path: str, d: JsonDict):
#   write_file(path, str(d))

# def read_jsonfile(path: str) -> JsonDict:
#   try:
#     return JsonDict(read_file)
#   except JSONDecodeError as e:
#     raise e


def edit_string(s: str = "") -> str:
  with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as f:
    n = f.name
    f.write(s)

  subprocess.run(["editor", n])
  s = read_file(n)

  os.remove(n)

  return s


def edit_dict(d: JsonDict = JsonDict()) -> JsonDict:
  valid = False
  while not valid:
    try:
      d = JsonDict(edit_string(str(d)))
    except json.JSONDecodeError:
      pass
    else:
      valid = True
  return d


def edit_connection_table(ct: ConnectionTable) -> ConnectionTable:
  s = ""
  valid = False
  while not valid:
    try:
      ct.update(edit_string(str(ct) + s))
    except ValueError as e:
      s = f"\n{e}"
    else:
      valid = True
  return ct


def prepare_directory(path: str):
  """ Clears existing config files in a directory """

  if not os.path.isdir(path):
    os.makedirs(path)
  else:
    _clean_directory(path)


def _clean_directory(path: str):
  files = os.listdir(path)
  for f in files:
    if os.path.isfile(os.path.join(path, f)):
      os.remove(os.path.join(path, f))


def delete_directory(path: str):
  """ Clears existing config files in a directory """

  if os.path.isdir(path):
    _clean_directory(path)
    os.rmdir(path)
