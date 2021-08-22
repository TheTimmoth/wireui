# database.py
# Basic database
# Author: Tim Schlottmann

from collections import UserDict
from json import dumps
from json import loads
from json import JSONDecodeError
from typing import Dict
from typing import Union

# DataDict = Dict[str, dict]

# StringDict = Dict[str, str]

# JsonString = str


class JsonDict(UserDict):
  def __init__(self,
               initialdata: Union[dict, str] = {},
               defaults: Union[dict, str] = {}):
    d = self.__getdict(defaults)
    d.update(self.__getdict(initialdata))
    super().__init__(d)

  @classmethod
  def __getdict(cls, data: Union[dict, str]) -> dict:
    if isinstance(data, dict):
      return data
    elif isinstance(data, str):
      if not data:
        data = "{}"
      try:
        return loads(data)
      except JSONDecodeError as e:
        raise e
    else:
      raise TypeError(
        f"Excpected type of data is dict or str. Got {type(data)}")

  def __repr__(self):
    return f"{type(self).__name__}({self.data})"

  def __str__(self):
    return dumps(self.data, indent=2)
