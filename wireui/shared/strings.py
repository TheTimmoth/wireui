from pkg_resources import resource_filename

from .language import get_language

from ..library import read_file
from ..library import JsonDict
from ..library import ReadOnlyJsonDict


class UI_Strings(ReadOnlyJsonDict):

  __instance = None

  @staticmethod
  def get_instance():
    """ Static access method. """
    if UI_Strings.__instance == None:
      UI_Strings()
    return UI_Strings.__instance

  def __init__(self):
    """ Virtually private constructor. """

    if UI_Strings.__instance != None:
      raise Exception("This class is a singleton!")
    else:
      d = JsonDict(read_file(resource_filename("wireui.shared", "ui.json")),
                   {})
      strings = d["en"]
      try:
        lang = d[get_language()]
      except KeyError:
        lang = {}
      for section in d["en"]:
        try:
          strings[section].update(lang[section])
        except KeyError:
          pass

      super().__init__(initialdata=strings, defaults={})
      UI_Strings.__instance = self
      strings = self

  def __getitem__(self, site_name) -> str:
    return super().__getitem__(site_name)


strings = UI_Strings.get_instance()
