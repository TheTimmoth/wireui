# database.py
# Basic database
# Author: Tim Schlottmann

from collections import UserDict
from json import dumps
from json import loads
from json import JSONDecodeError
from typing import Optional
from typing import Union

# DataDict = Dict[str, dict]

# StringDict = Dict[str, str]

# JsonString = str


class JsonDict(UserDict):
  def __init__(self,
               initialdata: Optional[Union[dict, str]] = {},
               defaults: Optional[Union[dict, str]] = {}):
    d = self.__getdict(defaults)
    d.update(self.__getdict(initialdata))
    super().__init__(d)

  @staticmethod
  def __getdict(data: Union[dict, str]) -> dict:
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


class ReadOnlyJsonDict(JsonDict):
  def __init__(self,
               initialdata: Optional[Union[dict, str]] = {},
               defaults: Optional[Union[dict, str]] = {}):
    super().__init__(initialdata=initialdata, defaults=defaults)

    self.__setitem__ = self.__readonly__
    self.__delitem__ = self.__readonly__
    self.pop = self.__readonly__
    self.popitem = self.__readonly__
    self.clear = self.__readonly__
    self.update = self.__readonly__
    self.setdefault = self.__readonly__

  def __readonly__(self, *args, **kwargs):
    raise RuntimeError(f"Modification of {type(self).__name__} prohibited")
