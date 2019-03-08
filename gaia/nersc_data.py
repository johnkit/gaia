from __future__ import absolute_import, division, print_function
from builtins import (
    bytes, str, open, super, range, zip, round, input, int, pow, object
)
import json
import urllib

from gaia.gaia_data import GaiaDataObject
from gaia.io.nersc_interface import NERSCInterface


class NERSCDataObject(GaiaDataObject):
    """Proxies either a file or a folder on nersc HPC machine

    """
    def __init__(self, reader, nersc_path, **kwargs):
        super(NERSCDataObject, self).__init__(**kwargs)
        self._reader = reader
        self.nersc_path = nersc_path
        # print('Created nersc object, resource_id: {}'.format(resource_id))

    def get_metadata(self, force=False):
        if force or not self._metadata:
            # metadata = NERSCInterface.get_instance().get_geometa(self.path)
            self._reader.load_metadata(self)
            # print('returned metadata: {}'.format(self._metadata))
        return self._metadata
