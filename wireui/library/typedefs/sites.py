# sites.py
# Wireguard sites
# Author: Tim Schlottmann

from json import dumps

from typing import NamedTuple
from typing import Union

from .dicts import JsonDict
from .dicts import JsonDict
from .peers import PeerItems
from .peers import Peers

#Evaluate TypedDict when python3.8 is available
SiteItems = dict


class Sites(JsonDict):
  """ Sites for wireguard """
  def __getitem__(self, site_name) -> SiteItems:
    return super().__getitem__(site_name)

  def __setitem__(self, site_name, site: SiteItems):
    super().__setitem__(site_name, site)
