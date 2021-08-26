# language.py
# Detect system language
# Author: Tim Schlottmann

import os
from locale import windows_locale


def get_language() -> str:
  if os.name in ["nt", "dos"]:
    from ctypes import windll
    dll = windll.kernel32
    lang = windows_locale[dll.GetUserDefaultUILanguage()].split("_")[0]
  else:
    lang = os.environ['LANG'].split("_")[0]
  return lang
