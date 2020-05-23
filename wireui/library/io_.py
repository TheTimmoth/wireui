import io
import json
import os
import subprocess
import tempfile

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
    return open(path, "r").read()
  except FileNotFoundError:
    return ""


# def write_jsonfile(path: str, d: JsonDict):
#   write_file(path, str(d))

# def read_jsonfile(path: str) -> JsonDict:
#   try:
#     return JsonDict(read_file)
#   except JSONDecodeError as e:
#     raise e


def edit_dict(d: JsonDict = JsonDict()) -> JsonDict:
  with tempfile.NamedTemporaryFile(mode='w+t', delete=False) as f:
    n = f.name
    f.write(str(d))

  valid = False
  while not valid:
    subprocess.run(["nano", n])
    try:
      d = JsonDict(read_file(n))
    except json.JSONDecodeError:
      pass
    else:
      valid = True

  os.remove(n)
  return d


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
