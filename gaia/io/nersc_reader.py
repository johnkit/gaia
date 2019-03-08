from __future__ import absolute_import, print_function
import os

from gaia import GaiaException
from gaia.nersc_data import NERSCDataObject
from gaia.io.gaia_reader import GaiaReader
from gaia.io.nersc_interface import NERSCInterface
import gaia.formats as formats
# import gaia.types as types


class NERSCReader(GaiaReader):
    """A subclass for proxying geodata files on NERSC HPC machines.

    Delegates I/O to NERSCInterface.
    Has limited capabilites based on functionality
    available from NERSC HPC machines.
    """
    def __init__(self, data_source, *args, **kwargs):
        """
        """
        super(NERSCReader, self).__init__(*args, **kwargs)
        self.url = None    # Gaia-specific URL, starts with nersc://
        self.path = None   # Path to file on NERSC global file system

        if isinstance(data_source, str):
            self.url = data_source
            self.path = self.__class__._parse_nersc_url(self.url)
        else:
            raise RuntimeError(
                'ERROR input data_source is not a string: {}'.format(data_source))

    @staticmethod
    def can_read(source, *args, **kwargs):
        if isinstance(source, str):
            nersc_path = NERSCReader._parse_nersc_url(source)
            if nersc_path is not None:
                # Todo Confirm that resource exists on NERSC global file system?
                return True

        # (else)
        return False

    def read(self, **kwargs):
        """Returns a NERSCDataset

        Doesn't actally load or move data; it remains on NERSC
        Todo: kwargs should probably be a union of raster and vector types,
        that get passed to NERSCDataset

        @return: NERSC dataset object
        """
        if self.url:
            nersc_path = self.__class__._parse_nersc_url(self.url)
            if nersc_path is None:
                raise GaiaException('Internal error - not a nersc url')

            return NERSCDataObject(self, nersc_path)

        raise GaiaException(
            'Internal error - should never reach end of NERSCReader.read()')
        return None

    def load_metadata(self, data_object):
        if self.path is None:
            self.path = this.__class__._parse_nersc_url(self.url)
        metadata = NERSCInterface.get_instance().load_metadata(self.path)
        data_object.set_metadata(metadata)

    @staticmethod
    def _parse_nersc_url(url):
        """

        Returns either None or path on NERSC global file system
        """
        if url is None:
            raise GaiaException('Internal error - url is None')

        # NERSC urls have "nersc://"" scheme and ".nersc" suffix

        nersc_scheme = 'nersc://'
        if not url.startswith(nersc_scheme):
            return None

        nersc_ending = '.nersc'
        if not url.endswith(nersc_ending):
            return None

        # Strip path out of url
        first_index = len(nersc_scheme)
        last_index = -len(nersc_ending)
        path = url[first_index:last_index]
        return path
