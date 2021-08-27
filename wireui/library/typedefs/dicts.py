""" Contains JsonDict and ReadOnlyJsonDict classes that help dealing with imported JSON files.

File: dicts.py
Author: Tim Schlottmann
Created: 2020-05-24
"""

from collections import UserDict
from json import dumps
from json import loads
from json import JSONDecodeError
from typing import Optional
from typing import Union


class JsonDict(UserDict):
  """ Dict that can be created from JSON Strings and presents its content in the same way

  This class is a dict that can return its content as a JSON compatible str. An instance
  of this class can also be created by such a string.
  During initialization initial and default data can be provided. If a key from default data
  is not present in initial data its added to the dict. The initial data will not be overwritten.

  A class can directly be initialzed with a string containing valid `JSON` Data for example
  from a JSON file.
  The `__str__` representation is also a valid JSON string that can be directly used to save it
  for example.

  Attributes:
    `initialdata`: Data that initializes the dict.
    `defaults`: Data that amends missing keys in initialdata. Does not overwrite data.
  """

  def __init__(self,
               initialdata: Optional[Union[dict, str]] = {},
               defaults: Optional[Union[dict, str]] = {}):
    """Inits JsonDict with no data by default"""

    d = self.__getdict(defaults)
    d.update(self.__getdict(initialdata))
    super().__init__(d)

  @staticmethod
  def __getdict(data: Union[dict, str]) -> dict:
    """ Private static method to convert the given data into a dict

    Args:
      data: A dict or string containing valid JSON data

    Returns:
      A dict that is generated from the given data.
    """

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

  def __repr__(self) -> str:
    """Returns a string representing the class"""

    return f"{type(self).__name__}({self.data})"

  def __str__(self) -> str:
    """Returns a string containing valid JSON data"""

    return dumps(self.data, indent=2)


class ReadOnlyJsonDict(JsonDict):
  """ Dict that can be created from JSON Strings and presents its content in the same way

  This class is a dict that can return its content as a JSON compatible str. An instance
  of this class can also be created by such a string.
  During initialization initial and default data can be provided. If a key from default data
  is not present in initial data its added to the dict. The initial data will not be overwritten.

  A class can directly be initialzed with a string containing valid `JSON` Data for example
  from a JSON file.
  The `__str__` representation is also a valid JSON string that can be directly used to save it
  for example.

  After initialization the content of this class cannot be changed.

  Attributes:
    `initialdata`: Data that initializes the dict.
    `defaults`: Data that amends missing keys in initialdata. Does not overwrite data.
  """

  def __init__(self,
               initialdata: Optional[Union[dict, str]] = {},
               defaults: Optional[Union[dict, str]] = {}):
    """Initialize dict with empty data by default"""

    super().__init__(initialdata=initialdata, defaults=defaults)

    self.__setitem__ = self.__readonly__
    self.__delitem__ = self.__readonly__
    self.pop = self.__readonly__
    self.popitem = self.__readonly__
    self.clear = self.__readonly__
    self.update = self.__readonly__
    self.setdefault = self.__readonly__

  def __readonly__(self, *args, **kwargs):
    """Covering all attempts to change the data of the dict"""

    raise RuntimeError(f"Modification of {type(self).__name__} prohibited")
