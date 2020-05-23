# wireguard.py
# Get keys from wg executable
# Author: Tim Schlottmannimport os

import subprocess
import collections

from .typedefs import Keys
from .typedefs import WireguardNotFoundError


def get_keys() -> Keys:
  """ Creates private, public and preshared key """

  privkey = _get_privkey()
  return Keys({
      "privkey": privkey,
      "pubkey": _get_pubkey(privkey),
      "psk": _get_psk(),
  })


def _get_privkey() -> str:
  """ Get a private key from wg """

  return _run(["wg", "genkey"])


def _get_pubkey(private: str) -> str:
  """ Get a public key from wg """

  return _run(["wg", "pubkey"], input=private.encode("utf-8"))


def _get_psk() -> str:
  """ Get a presharedkey from wg """

  return _run(["wg", "genpsk"])


def _run(*args, **kwargs) -> str:
  """ Run a program on the OS and collect output """

  try:
    return subprocess.run(
        *args, stdout=subprocess.PIPE,
        **kwargs).stdout.decode("utf-8").strip()
  except FileNotFoundError as e:
    raise WireguardNotFoundError(
        "Wireguard not found. Please install it or add it to $PATH")
