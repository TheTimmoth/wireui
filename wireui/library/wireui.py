# wire_interface.py
# Get keys from wg Write wireguard config files
# Author: Tim Schlottmann

from os import path
from typing import NamedTuple
from typing import Optional

# from .io_ import JSONDecodeError

from .config import delete_config
from .config import write_config

from .io_ import read_file
from .io_ import write_file

from .keys import get_keys

from .typedefs import JSONDecodeError
from .typedefs import PeerItems
from .typedefs import PeerDoesExistError
from .typedefs import PeerDoesNotExistError
from .typedefs import Peers
from .typedefs import Settings
from .typedefs import SettingDoesNotExistError
from .typedefs import SiteItems
from .typedefs import SiteDoesExistError
from .typedefs import SiteDoesNotExistError
from .typedefs import Sites


class Site(NamedTuple):
  name: str
  endpoint: str
  port: int
  ip_networks: str
  main_peer_name: str
  client_peer_names: list


class WireUI():
  """ Class for managing wireguard config files """

  def __init__(self, settings_path: Optional[str] = None):
    _DEFAULT_SETTINGS = {
        "verbosity": 0,
        "sites_file_path": "./sites.json",
        "wg_config_path": "./wg",
        "editor": "editor",
    }
    if settings_path:
      self.settings_path = settings_path
      try:
        self._settings = Settings(read_file(settings_path), _DEFAULT_SETTINGS)
      except JSONDecodeError as e:
        raise e
    else:
      self._settings = Settings(defaults=_DEFAULT_SETTINGS)

    self._sites = Sites(read_file(self._settings.get("sites_file_path")))

  def get_sites(self) -> list:
    """ Get all existing sites """

    return list(self._sites)

  def add_site(self, site: Site):
    """ Add a new site and creates its config files """

    if site.name in self._sites:
      raise SiteDoesExistError(site.name)

    peers = Peers()
    try:
      peers[site.main_peer_name] = PeerItems({"keys": get_keys()})
    except PeerDoesExistError as e:
      raise e

    for p in site.client_peer_names:
      try:
        peers[p] = PeerItems({"keys": get_keys()})
      except PeerDoesExistError as e:
        raise e

    self._sites[site.name] = SiteItems({
        "endpoint": site.endpoint,
        "ip_networks": site.ip_networks,
        "port": site.port,
        "main_peer_name": site.main_peer_name,
        "peers": peers
    })

  def delete_site(self, name: str):
    """ Delete a site """

    if name not in self._sites:
      raise SiteDoesNotExistError(name)

    del self._sites[name]

  def site_exists(self, name: str) -> bool:
    """ Check if a site does exist """

    return name in self._sites

  def get_number_of_sites(self) -> int:
    """ Get the number of existing sites """

    return len(self._sites)

  def get_peers(self, site_name: str) -> list:
    """ Get all existing peers from a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    return list(self._sites[site_name]["peers"])

  def add_peer(self, site_name: str, peer_name: str):
    """ Add a peer to a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    if peer_name in self._sites[site_name]["peers"]:
      raise PeerDoesExistError(peer_name)

    self._sites[site_name]["peers"][peer_name] = PeerItems({
        "keys": get_keys()
    })

  def add_peers_from_list(self, site_name: str, peer_names: list):
    """ Add multiple peers to a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    for p in peer_names:
      try:
        self.add_peer(site_name, p)
      except PeerDoesExistError as e:
        raise e

  def delete_peer(self, site_name: str, peer_name: str):
    """ Delete a peer from a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    if peer_name not in self._sites[site_name]["peers"]:
      raise PeerDoesNotExistError(peer_name)

    del self._sites[site_name]["peers"][peer_name]

  def rekey_peer(self, site_name: str, peer_name: str):
    """ Create new keys for a peer from a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    if peer_name not in self._sites[site_name]["peers"]:
      raise PeerDoesNotExistError(peer_name)

    self._sites[site_name]["peers"][peer_name] = PeerItems({
        "keys": get_keys()
    })

  def peer_exists(self, site_name: str, peer_name: str) -> bool:
    """ Check if a peer exists in a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    return peer_name in self._sites[site_name]["peers"]

  def get_number_of_peers(self, site_name: str) -> int:
    """ Get the number of peers in a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)
    return len(self._sites[site_name]["peers"])

  def create_wireguard_config(self, site_name: str) -> list:
    """ Write the wireguard config files """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    return write_config(self._sites[site_name],
                        path.join(self._settings["wg_config_path"], site_name))

  def delete_wireguard_config(self, site_name: str):
    """ Check if a peer exists in a site """

    if site_name not in self._sites:
      raise SiteDoesNotExistError(site_name)

    delete_config(site_name,
                  path.join(self._settings.get("wg_config_path"), site_name))

  def get_settings(self, setting: str) -> list:
    """ Get all setting """

    return list(self._settings)

  def get_setting(self, setting: str):
    """ Get a setting """

    if setting not in self._settings:
      raise SettingDoesNotExistError

    return self._settings[setting]

  def write_settings_to_file(self):
    write_file(self.settings_path, str(self._settings))

  def write_sites_to_file(self):
    write_file(self._settings["sites_file_path"], str(self._sites))
