import os


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


def prepare_directory(path: str):
  """ Clears existing config files in a directory """

  if not os.path.isdir(path):
    os.makedirs(path)
  else:
    __clean_directory(path)


def __clean_directory(path: str):
  files = os.listdir(path)
  for f in files:
    if os.path.isfile(os.path.join(path, f)):
      os.remove(os.path.join(path, f))


def delete_directory(path: str):
  """ Clears existing config files in a directory """

  if os.path.isdir(path):
    __clean_directory(path)
    os.rmdir(path)
