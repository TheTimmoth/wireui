# tables.py
# Table for wireguard
# Author: Tim Schlottmann

from typing import Union

from .exceptions import PeerDoesNotExistError

from .result import MESSAGE_LEVEL
from .result import Message
from .result import MessageContent
from .result import Result


class Table():
  """ n x m table """
  def __init__(self,
               n: int,
               m: int,
               row_names: list = [],
               column_names: list = []):
    if len(row_names) != n and row_names != []:
      raise ValueError("Dimension mismatch: len(row_names) != n")
    if len(column_names) != m and column_names != []:
      raise ValueError("Dimension mismatch: len(column_names) != m")

    self.n = n
    self.m = m

    # Create n x m matrix
    self.content = [None] * self.n
    for i in range(self.n):
      self.content[i] = [None] * self.m

    self.row_names = row_names
    self.column_names = column_names

    # Get parameters from names
    if self.row_names != []:
      self.row_names_lengths = [0] * n
      self.row_names_max_length = 0
      for i in range(n):
        self.row_names_lengths[i] = len(self.row_names[i])
        if self.row_names_lengths[i] > self.row_names_max_length:
          self.row_names_max_length = self.row_names_lengths[i]

    if self.column_names != []:
      self.column_names_lengths = [0] * m
      self.column_names_max_length = 0
      for i in range(m):
        self.column_names_lengths[i] = len(self.column_names[i])
        if self.column_names_lengths[i] > self.column_names_max_length:
          self.column_names_max_length = self.column_names_lengths[i]

  def __repr__(self):
    return f"{type(self).__name__}({self.n}, {self.m}, {self.row_names}, {self.column_names})"

  def __str__(self):
    s = ""

    # Print column headings (only if there are any)
    if len(self.column_names) > 0:
      for i in range(self.row_names_max_length):
        s += " "
      for i in range(len(self.column_names)):
        s += f" {self.column_names[i]}"
      s += "\n"

    # Print rows (only if there are any)
    for i in range(self.n):
      if len(self.row_names) > 0:
        for j in range(self.row_names_max_length - self.row_names_lengths[i]):
          s += " "
        s += self.row_names[i]
      for j in range(self.m):
        s += f" {self.content[i][j]}"
        if len(self.column_names) > 0 and len(str(
            self.content[i][j])) < self.column_names_lengths[j]:
          for _ in range(self.column_names_lengths[j] -
                         len(str(self.content[i][j]))):
            s += " "
      s += "\n"

    #Remove last new line
    s = s[:-1]

    return s

  def getitem(self, i: int, j: int) -> any:
    """ Get the value of the item in row i and column j """
    return self.content[i][j]

  def setitem(self, i: int, j: int, v: any):
    """ Set the item in row i and column j to value v """
    self.content[i][j] = v

  def setrow(self, i: int, r: list):
    if len(r) == self.m:
      self.content[i] = r
    else:
      raise ValueError(
        f"Dimension mismatch: len(r) ({len(r)}) != self.m ({self.m})")


class CONNECTION_TABLE_MESSAGE_TYPE():
  @property
  def DIMENSION_MISMATCH():
    return 0

  @property
  def SELF_CONNECTION():
    return 1

  @property
  def MAIN_PEER_MISSING():
    return 2

  @property
  def MAIN_PEER_NOT_EXISTS():
    return 3

  @property
  def MAIN_PEER_NOT_OUTGOING():
    return 4


class ConnectionTableMessageContent(MessageContent):
  message_type: int
  peer: str
  i: int
  j: int
  actual: Union[int, str]
  should: Union[int, str]


ConnectionTableMessage = Message[ConnectionTableMessageContent]


class ConnectionTable(Table):
  """ ConnectionTable for peers """
  def __init__(self, peer_names: list):
    super().__init__(len(peer_names),
                     len(peer_names) + 1, peer_names,
                     peer_names + ["main_peer"])
    for i in range(self.n):
      for j in range(self.n):
        self.setitem(i, j, 0)
      self.setitem(i, self.m - 1, "None")

  def __repr__(self):
    return f"{type(self).__name__}({self.row_names})"

  def setitem(self, i: int, j: int, v: Union[int, str]):
    """ Set the item in row i and column j to value v

        Please execute check_integrity afterwards to make sure changed data is still valid """

    super().setitem(i, j, v)

  def update(self, s: str) -> Result:
    """ Updates the table with a str representation of a ConnectionTable object """
    r = Result()

    # Split lines and remove first line
    s = s.splitlines()
    s.pop(0)

    for i in range(self.n):
      # Separate connection elements
      s[i] = s[i][self.row_names_max_length + 1:]
      s[i] = s[i].split()

      if len(s[i]) != self.m:
        r.append(
          ConnectionTableMessage(
            message_level=MESSAGE_LEVEL.ERROR,
            message=ConnectionTableMessageContent(
              message_type=CONNECTION_TABLE_MESSAGE_TYPE.DIMENSION_MISMATCH,
              peer="",
              i=i,
              j=0,
              actual=len(s[i]),
              should=self.m)))
        continue

      # Update table
      for j in range(self.m):
        if j < self.m - 1:
          self.setitem(i, j, int(s[i][j]))
        else:
          self.setitem(i, j, s[i][j])

    self.__check_integrity(r)

    return r

  def get_outgoing_connected_peers(self, name: str) -> list:
    """ Get a list of all peers that peer 'name' has an outgoing connection to """
    # Get row index for peer
    row = -1
    for i in range(self.n):
      if self.column_names[i] == name:
        row = i
        break
    if row == -1:
      raise PeerDoesNotExistError(name)

    # List all peers with an outgoing connection to that peer
    l = []
    for i in range(self.n):
      if self.getitem(row, i):
        l.append(self.column_names[i])

    return l

  def get_main_peer(self, name: str) -> str:
    """ Get the main peer for outgoing connections for a peer """
    # Get row index for peer
    row = -1
    for i in range(self.n):
      if self.column_names[i] == name:
        row = i
        break
    if row == -1:
      raise PeerDoesNotExistError(name)

    return (self.getitem(row, self.m - 1))

  def get_ingoing_connected_peers(self, name: str) -> list:
    """ Get a list of all peers that peer 'name' has an ingoing connection from """
    # Get column index for peer
    column = -1
    for i in range(self.m):
      if name == self.column_names[i]:
        column = i
        break

    if column == -1:
      raise PeerDoesNotExistError(name)

    # List all peers with an ingoing connection from that peer
    l = []
    for i in range(self.n):
      if self.getitem(i, column):
        l.append(self.row_names[i])

    return l

  def __check_integrity(self, r: Result):
    """ Check if the table has invalid entries """

    #Check if all diagonal elements are zero
    for i in range(self.n):
      if self.getitem(i, i) == 1:
        self.setitem(i, i, 0)
        r.append(
          ConnectionTableMessage(
            message_level=MESSAGE_LEVEL.ERROR,
            message=ConnectionTableMessageContent(
              message_type=CONNECTION_TABLE_MESSAGE_TYPE.SELF_CONNECTION,
              peer=self.row_names[i],
              i=i,
              j=i,
              actual=1,
              should=0)))

    # Check main_peers
    for i in range(self.n):
      # If there are outgoing peers...
      if len(self.get_outgoing_connected_peers(
          self.row_names[i])) > 0 or self.getitem(i, self.m - 1) != "None":

        # ... check if there is a main_peer
        if self.getitem(i, self.m - 1) == "None":
          self.setitem(i, self.m - 1,
                       self.get_outgoing_connected_peers(self.row_names[i])[0])
          r.append(
            ConnectionTableMessage(
              message_level=MESSAGE_LEVEL.ERROR,
              message=ConnectionTableMessageContent(
                message_type=CONNECTION_TABLE_MESSAGE_TYPE.MAIN_PEER_MISSING,
                peer=self.row_names[i],
                i=i,
                j=self.m - 1,
                actual="",
                should=self.getitem(i, self.m - 1))))

        # ... check if the main_peer exists
        if self.getitem(i, self.m - 1) not in self.row_names:
          # Correct to the first outgoing peer if there is one
          if self.get_outgoing_connected_peers(self.row_names[i]):
            self.setitem(
              i, self.m - 1,
              self.get_outgoing_connected_peers(self.row_names[i])[0])
            r.append(
              ConnectionTableMessage(
                message_level=MESSAGE_LEVEL.ERROR,
                message=ConnectionTableMessageContent(
                  message_type=CONNECTION_TABLE_MESSAGE_TYPE.
                  MAIN_PEER_NOT_EXISTS,
                  peer=self.row_names[i],
                  i=i,
                  j=self.m - 1,
                  actual="",
                  should=self.getitem(i, self.m - 1))))
          # Correct to "None" otherwise
          else:
            self.setitem(i, self.m - 1, "None")
            r.append(
              ConnectionTableMessage(
                message_level=MESSAGE_LEVEL.ERROR,
                message=ConnectionTableMessageContent(
                  message_type=CONNECTION_TABLE_MESSAGE_TYPE.
                  MAIN_PEER_NOT_EXISTS,
                  peer=self.row_names[i],
                  i=i,
                  j=self.m - 1,
                  actual="",
                  should="None")))

        # ... check if the main_peer is outgoing
        elif self.getitem(i,
                          self.m - 1) not in self.get_outgoing_connected_peers(
                            self.row_names[i]):
          j = 0
          for name in self.column_names:
            if self.getitem(i, self.m - 1) == name:
              self.setitem(i, j, 1)
              break
            j += 1
          r.append(
            ConnectionTableMessage(
              message_level=MESSAGE_LEVEL.ERROR,
              message=ConnectionTableMessageContent(
                message_type=CONNECTION_TABLE_MESSAGE_TYPE.
                MAIN_PEER_NOT_OUTGOING,
                peer=self.row_names[i],
                i=i,
                j=j,
                actual=0,
                should=1)))
