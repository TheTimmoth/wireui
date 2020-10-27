# settings.py
# Settings
# Author: Tim Schlottmann

from typing import Any

from .dicts import JsonDict


class Settings(JsonDict):
  """ Settings of the app """
  def __getitem__(self, setting_name) -> Any:
    return super().__getitem__(setting_name)

  def __setitem__(self, setting_name, setting):
    super().__setitem__(setting_name, setting)
