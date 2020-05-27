import unittest
from os import remove
from os import makedirs
from os import rmdir
from os import path

from .io_ import write_file
from .io_ import read_file
from .io_ import prepare_directory
from .io_ import delete_directory


class TestIO(unittest.TestCase):
  def test_file(self):
    #Preparation
    s = "TEST"
    p = "./testfile"

    #Test write_file and read
    write_file(p, s)
    f = read_file(p)
    self.assertEqual(f, s, f"{f} was read from {p}, should have been {s}")

    #Clean up
    remove(p)

  def test_directory(self):
    #Preparation
    p = "./testfolder/"
    if path.isdir(p):
      rmdir(p)

    #Test prepare_directory
    prepare_directory(p)
    self.assertTrue(path.isdir(p), f"{p} has not been created")

    #Preparation
    created = []
    for i in range(3):
      with open(path.join(p, str(i)), "w"):
        pass
      created.append(path.join(p, str(i)))

    #Test _clean_directory
    prepare_directory(p)
    for f in created:
      self.assertFalse(path.isfile(f), f"{f} has not been deleted")

    #Test delete_directory
    delete_directory(p)
    self.assertFalse(path.isdir(p), f"{p} has not been deleted")


if __name__ == "__main__":
  unittest.main()
