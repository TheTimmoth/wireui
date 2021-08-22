class Error(Exception):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


class KeyExistenceError(Error):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)


class KeyDoesExistError(KeyExistenceError):
  def __init__(self, key_name):
    super().__init__(f"{key_name} does already exist")


class KeyDoesNotExistError(KeyExistenceError):
  def __init__(self, key_name):
    super().__init__(f"{key_name} does not exist")


class PeerDoesExistError(KeyDoesExistError):
  pass


class PeerDoesNotExistError(KeyDoesNotExistError):
  pass


class SettingDoesExistError(KeyDoesExistError):
  pass


class SettingDoesNotExistError(KeyDoesNotExistError):
  pass


class SiteDoesExistError(KeyDoesExistError):
  pass


class SiteDoesNotExistError(KeyDoesNotExistError):
  pass


class WireguardNotFoundError(Error):
  pass


class DataIntegrityError(Error):
  pass


class IPNetworkError(DataIntegrityError):
  pass


class DNSError(DataIntegrityError):
  pass


class AdditionalAllowedIPError(DataIntegrityError):
  pass


class PeerConnectionError(DataIntegrityError):
  pass


class EndpointError(DataIntegrityError):
  pass


class PortError(DataIntegrityError):
  pass
