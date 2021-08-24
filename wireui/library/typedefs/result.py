from collections import UserList
from typing import Generic, Iterable, List, NamedTuple, Optional, TypeVar


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

U = TypeVar("U")


class Message(Generic[U]):
  def __init__(self, message_level: int, message: U):
    self.message_level: int = message_level
    self.content: U = message

  def get_message_level(self) -> int:
    return self.message_level

  def get_message(self) -> U:
    return self.content

  def __str__(self) -> str:
    return f"({self.message_level}, {self.content})"

  def __repr__(self) -> str:
    return f"{type(self).__name__}{self.__str__()}"


T = TypeVar("T")


class Result(Generic[T]):
  def __init__(self, initlist: Optional[Iterable] = []):
    self.l: List[T] = list(initlist)

  def get_success(self, warnings_as_errors: Optional[bool] = False):
    for m in self.l:
      if m.message_level == MESSAGE_LEVEL.ERROR or (
          m.message_level == MESSAGE_LEVEL.WARNING and warnings_as_errors):
        return False
    return True

  def append(self, item: T):
    self.l.append(item)

  def __getitem__(self, index: int) -> T:
    return self.l[index]

  def __setitem__(self, index: int, value: T):
    self.l[index] = value

  def __len__(self) -> int:
    return len(self.l)

  def __str__(self) -> str:
    return str(self.l)

  def __repr__(self) -> str:
    return f"{type(self).__name__}({self.__str__()})"

  def __bool__(self) -> bool:
    return bool(self.l)
