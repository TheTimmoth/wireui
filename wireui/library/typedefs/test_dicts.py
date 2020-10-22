import unittest
from .dicts import JsonDict


class TestJsonDict(unittest.TestCase):
  def test_creation(self):
    # Test creation from dict
    d = JsonDict({"A": 1, "B": 2})
    self.assertEqual(d["A"], 1)
    self.assertEqual(d["B"], 2)

    # Test creation from json string
    d = JsonDict("{\"A\": 1, \"B\": 2}")
    self.assertEqual(d["A"], 1)
    self.assertEqual(d["B"], 2)

  def test_defaults(self):
    d = JsonDict({"A": 1, "B": 2}, {"B": 4, "C": 3})
    self.assertEqual(d["A"], 1)
    self.assertEqual(d["B"], 2)
    self.assertEqual(d["C"], 3)

  def test_repr(self):
    d = JsonDict({"A": 1, "B": 2})
    self.assertEqual(repr(d), "JsonDict({'A': 1, 'B': 2})")

    d = JsonDict("{\"A\": 1, \"B\": 2}")
    self.assertEqual(repr(d), "JsonDict({'A': 1, 'B': 2})")

  def test_str(self):
    d = JsonDict({"A": 1, "B": 2})
    self.assertEqual(str(d), "{\n  \"A\": 1,\n  \"B\": 2\n}")


if __name__ == "__main__":
  unittest.main()
