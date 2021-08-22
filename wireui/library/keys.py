# wireguard.py
# Get keys from wg executable
# Author: Tim Schlottmannimport os

import subprocess
import collections

from .typedefs import Keys
from .typedefs import WireguardNotFoundError

__wg_exec = ""


def get_keys() -> Keys:
  """ Creates private, public and preshared key """

  privkey = __get_privkey()
  return Keys({
    "privkey": privkey,
    "pubkey": __get_pubkey(privkey),
    "psk": __get_psk(),
  })

def set_wg_exec(wg_exec: str):
  global __wg_exec
  __wg_exec = wg_exec


def __get_privkey() -> str:
  """ Get a private key from wg """

  return __run([__wg_exec, "genkey"])


def __get_pubkey(private: str) -> str:
  """ Get a public key from wg """

  return __run([__wg_exec, "pubkey"], input=private.encode("utf-8"))


def __get_psk() -> str:
  """ Get a presharedkey from wg """

  return __run([__wg_exec, "genpsk"])


def __run(*args, **kwargs) -> str:
  """ Run a program on the OS and collect output """

  try:
    return subprocess.run(*args, stdout=subprocess.PIPE,
                          **kwargs).stdout.decode("utf-8").strip()
  except FileNotFoundError:
    raise WireguardNotFoundError(
      "Wireguard not found. Please install it and/or make shure it is available via $PATH"
    )
