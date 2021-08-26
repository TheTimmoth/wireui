from collections import UserList
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

  def get_message_level(self) -> int:
    return self.message_level

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
  def get_success(self, warnings_as_errors: Optional[bool] = False):
    success = True
    for r in self.l:
      success |= r.get_success()
    return success
