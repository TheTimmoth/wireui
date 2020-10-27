import unittest
from .tables import Table, ConnectionTable


class TestTable(unittest.TestCase):
  def test_creation(self):
    #Test table creation
    Table(3, 4)
    Table(3, 4, row_names=["Alpha", "Beta", "Gamma"])
    Table(3, 4, column_names=["Alpha", "Beta", "Gamma", "Delta"])
    t = Table(3, 4, ["Alpha", "Beta", "Gamma"],
              ["Alpha", "Beta", "Gamma", "Delta"])

    #Test initialization values
    for i in range(3):
      for j in range(4):
        self.assertEqual(None, t.content[i][j])

  def test_getter_and_setter(self):
    t = Table(3, 4, ["Alpha", "Beta", "Gamma"],
              ["Alpha", "Beta", "Gamma", "Delta"])

    r = [1, 2, 3, 4]
    for i in range(3):
      for j in range(4):
        self.assertEqual(None, t.getitem(i, j))
        t.setitem(i, j, "a")
        self.assertEqual("a", t.getitem(i, j))
      t.setrow(i, r)
      for j in range(4):
        self.assertEqual(r[j], t.getitem(i, j))

  def test_str(self):
    t = Table(3, 4, ["Alpha", "Beta", "Gamma"],
              ["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "      Alpha Ypsilon Beta Delta\nAlpha None  None    None None \n Beta None  None    None None \nGamma None  None    None None "
    self.assertEqual(s, str(t))

  def test_repr(self):
    t = Table(3, 4, ["Alpha", "Beta", "Gamma"],
              ["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "Table(3, 4, ['Alpha', 'Beta', 'Gamma'], ['Alpha', 'Ypsilon', 'Beta', 'Delta'])"
    self.assertEqual(s, repr(t))

  def test_error(self):
    self.assertRaises(ValueError, Table, 3, 4, ["Alpha"])
    self.assertRaises(ValueError, Table, 3, 4, [], ["Alpha"])
    self.assertRaises(ValueError, Table, 3, 4, ["Alpha"], ["Alpha"])


class TestConnectionTable(unittest.TestCase):
  def test_creation(self):
    #Test table creation
    t = ConnectionTable(["Alpha", "Beta", "Gamma", "Delta"])

    #Test initialization values
    for i in range(4):
      for j in range(4):
        self.assertEqual(0, t.content[i][j])

    for i in range(4):
      self.assertEqual(None, t.content[i][4])

  def test_getter_and_setter(self):
    t = ConnectionTable(["Alpha", "Beta", "Gamma", "Delta"])

    r = [1, 2, 3, 4, "Alpha"]
    for i in range(4):
      for j in range(4):
        self.assertEqual(0, t.getitem(i, j))
        if (i == j):
          pass
        else:
          t.setitem(i, j, 1)
          self.assertEqual(1, t.getitem(i, j))
      t.setrow(i, r)
      for j in range(5):
        self.assertEqual(r[j], t.getitem(i, j))

  def test_str(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     0       0    0     None     \nYpsilon 0     0       0    0     None     \n   Beta 0     0       0    0     None     \n  Delta 0     0       0    0     None     "
    self.assertEqual(s, str(t))

  def test_repr(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "ConnectionTable(['Alpha', 'Ypsilon', 'Beta', 'Delta'])"
    self.assertEqual(s, repr(t))

  def test_update(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     0       0    0     None     \nYpsilon 0     0       0    0     None     \n   Beta 0     0       0    0     None     \n  Delta 0     0       0    0     None     "
    self.assertEqual(s, str(t))

    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     0       0    0     None     \nYpsilon 1     0       1    1     Delta    \n   Beta 1     1       0    1     Delta    \n  Delta 1     1       1    0     Beta     "
    t.update(s)
    self.assertEqual(s, str(t))

    for i in range(t.n):
      for j in range(t.n):
        self.assertTrue(isinstance(t.getitem(i, j), int))
      if i == 0:
        self.assertTrue(t.getitem(i, t.m - 1) is None)
      else:
        self.assertTrue(isinstance(t.getitem(i, t.m - 1), str))

  def test_get_outgoing_connected_peers(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     1       1    1     Delta    \nYpsilon 1     0       1    1     Delta    \n   Beta 1     1       0    1     Delta    \n  Delta 1     1       1    0     Beta     "
    t.update(s)

    l = t.get_outgoing_connected_peers("Alpha")
    self.assertEqual(["Ypsilon", "Beta", "Delta"], l)

  def test_get_ingoing_connected_peers(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     1       1    1     Delta    \nYpsilon 1     0       1    1     Delta    \n   Beta 1     1       0    1     Delta    \n  Delta 1     1       1    0     Beta     "
    t.update(s)

    l = t.get_ingoing_connected_peers("Ypsilon")
    self.assertEqual(["Alpha", "Beta", "Delta"], l)

  def test_get_main_peer(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     1       1    1     Delta    \nYpsilon 1     0       1    1     Delta    \n   Beta 1     1       0    1     Delta    \n  Delta 1     1       1    0     Beta     "
    t.update(s)

    self.assertEqual("Delta", t.get_main_peer("Alpha"))

  def test_error(self):
    t = ConnectionTable(["Alpha", "Ypsilon", "Beta", "Delta"])
    self.assertRaises(ValueError, t.setitem, 1, 1, 1)
    self.assertRaises(ValueError, t.setitem, 1, 4, 1)

    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 0     1       1    1     Delta    \nYpsilon 1     0       1    1     Delta    \n   Beta 1     1       0    1     Beta     \n  Delta 1     1       1    0     Beta     "
    self.assertRaises(ValueError, t.update, s)

    s = "        Alpha Ypsilon Beta Delta main_peer\n  Alpha 1     1       1    1     Delta    \nYpsilon 1     0       1    1     Delta    \n   Beta 1     1       0    1     Delta    \n  Delta 1     1       1    0     Beta     "
    self.assertRaises(ValueError, t.update, s)


if __name__ == "__main__":
  unittest.main()
