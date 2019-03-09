from __future__ import absolute_import, division, print_function
from builtins import (
    bytes, str, open, super, range, zip, round, input, int, pow, object
)

sqlengines = {}


class GaiaException(Exception):
    """
    Base Gaia exception class
    """
    pass


class MissingParameterError(GaiaException):
    """Raise when a required parameter is missing"""
    pass


class MissingDataException(GaiaException):
    """Raise when required data is missing"""
    pass


class UnhandledOperationException(GaiaException):
    """Raise when required data is missing"""
    pass


class UnsupportedFormatException(GaiaException):
    """Raise when an unsupported data format is used"""
    pass

class GaiaProcessError(GaiaException):
    """Raise when a process error occurs"""
    pass


def get_uri_extension(uripath):
    idx = uripath.rfind('.')
    if idx >= 0:
        return uripath[idx + 1:]
    return None
