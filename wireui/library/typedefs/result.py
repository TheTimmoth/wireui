from collections import UserDict
from typing import Generic, Iterable, List, NamedTuple, Optional, TypeVar

from .list import BasicList


class __MessageLevel(NamedTuple):
  ERROR: int
  WARNING: int
  INFORMATION: int


MESSAGE_LEVEL = __MessageLevel(
  ERROR=0,
  WARNING=1,
  INFORMATION=2,
)

MessageContent = NamedTuple

T = TypeVar("T")


class Message(Generic[T]):
  def __init__(self, message_level: int, message: T):
    self.message_level: int = message_level
    self.content: T = message

  # TODO: use property
  def get_message_level(self) -> int:
    return self.message_level

  # TODO: use property
  def get_message(self) -> T:
    return self.content

  def __str__(self) -> str:
    return f"({self.message_level}, {self.content})"

  def __repr__(self) -> str:
    return f"{type(self).__name__}{self.__str__()}"


class Result(BasicList[Message]):
  def get_success(self, warnings_as_errors: Optional[bool] = False):
    for m in self.l:
      if m.message_level == MESSAGE_LEVEL.ERROR or (
          m.message_level == MESSAGE_LEVEL.WARNING and warnings_as_errors):
        return False
    return True


class ResultList(BasicList[Result]):
  def __init__(self, name: str, initlist: Optional[Iterable] = []):
    self.__name = name
    super().__init__(initlist=initlist)

  @property
  def name(self):
    return self.__name

  def get_success(self, warnings_as_errors: Optional[bool] = False):
    success = True
    for r in self.l:
      success &= r.get_success(warnings_as_errors)
    return success


class DataIntegrityMessage():
  def __init__(self) -> None:
    self.__site_result = ResultList("")
    self.__peer_results: List[ResultList] = []

  @property
  def name(self):
    return self.__site_result.name

  @property
  def site_result(self) -> ResultList:
    return self.__site_result

  @property
  def peer_results(self) -> List[ResultList]:
    return self.__peer_results

  @site_result.setter
  def site_result(self, rl: ResultList):
    self.__site_result = rl

  @peer_results.setter
  def peer_results(self, rl: ResultList):
    self.__peer_results = rl

  def get_success(self, warnings_as_errors: Optional[bool] = False):
    success = self.site_result.get_success(warnings_as_errors)
    for rl in self.__peer_results:
      success &= rl.get_success()
    return success


class DataIntegrityResult(UserDict):
  def __init__(self):
    self.__warnings_as_errors = False
    super().__init__()

  def get_success(self, warnings_as_errors: Optional[bool] = False):
    success = True
    for site in self.data:
      success &= self.data[site].get_success(warnings_as_errors)
      if not success:
        return success
    return success

  def setitem(self, data_integrity_message: DataIntegrityMessage):
    return super().__setitem__(data_integrity_message.name,
                               data_integrity_message)

  def __getitem__(self, site_name: str) -> DataIntegrityMessage:
    return super().__getitem__(site_name)

  def __setitem__(self, site_name: str,
                  data_integrity_message: DataIntegrityMessage):
    return super().__setitem__(site_name, data_integrity_message)
