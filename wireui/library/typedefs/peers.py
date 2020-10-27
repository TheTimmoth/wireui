# peers.py
# Peers for wireguard
# Author: Tim Schlottmann

# from collections import UserDict  # creates not JSON serializable error
from typing import Dict

# TODO: Evaluate TypedDict when python3.8 is available
Keys = dict

# TODO: Evaluate TypedDict when python3.8 is available
RedirectAllTraffic = dict

# TODO: Evaluate TypedDict when python3.8 is available
PeerItems = dict


class Peers(dict):
  """ Peers for wireguard """
  def __getitem__(self, peer_name) -> PeerItems:
    return super().__getitem__(peer_name)

  def __setitem__(self, peer_name, peer: PeerItems):
    super().__setitem__(peer_name, peer)
