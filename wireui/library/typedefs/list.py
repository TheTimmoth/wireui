from typing import Generic, Iterable, List, Optional, TypeVar

T = TypeVar("T")


class BasicList(Generic[T]):
  def __init__(self, initlist: Optional[Iterable] = []):
    self.l: List[T] = list(initlist)

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
