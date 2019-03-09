from __future__ import absolute_import, division, print_function
from builtins import (
    bytes, str, open, super, range, zip, round, input, int, pow, object
)
import sys
from urllib.parse import urlencode

import geojson

import gaia.types
import gaia.validators as validators
from gaia.util import GaiaException, GaiaProcessError
from gaia.gaia_data import GaiaDataObject
from gaia.nersc_data import NERSCDataObject
from gaia.io.nersc_reader import NERSCReader
from gaia.process_registry import register_process


def validate_nersc_crop(v):
    """
    Verify that inputs are all girder objects
    """
    def validator(inputs=[], args={}):
        # First object must be NERSCDataObject
        if (type(inputs[0]) is not NERSCDataObject):
            raise GaiaException('nersc process requires NERSCDataObject')

        # Second object must have vector geometry,
        # and, for now, be on the local filesystem
        geom_input = inputs[1]
        if (isinstance(geom_input, GaiaDataObject)):
            if geom_input.is_remote():
                raise GaiaException('crop geometry from remote object not supported')

            elif geom_input.get_datatype() != gaia.types.VECTOR:
                template = """nersc process cannot use datatype \"{}\"" \
                    for crop geometry"""
                raise GaiaException(template.format(geom_input.get_datatype()))

        # Otherwise call up the chain to let parent do common validation
        return v(inputs, args)

    return validator


@register_process('crop')
@validate_nersc_crop
def compute_nersc_crop(inputs=[], args_dict={}):
    """
    Runs the subset computation on NERSC machine
    """
    # Current support is single dataset
    dataset = inputs[0]

    # Format geometry as geojson feature collection
    geometry = inputs[1]
    if isinstance(geometry, GaiaDataObject):
        geojson_data = inputs[1].get_data().__geo_interface__
    elif geometry.get('type') == 'FeatureCollection':
        geojson_data = geometry
    elif geometry.get('coordinates') is not None:
        # Create feature collection
        feature = geojson.Feature(geometry=geometry)
        geojson_data = geojson.FeatureCollection(features=[feature])
    else:
        raise GaiaProcessError('Unrecognized crop geometry')

    output_path = args_dict.get('output_path', 'crop_output.tif')

    from gaia.io.nersc_interface import NERSCInterface
    nersc = NERSCInterface.get_instance()
    nersc.compute_crop(dataset.nersc_path, geojson_data, output_path)

    # If no exception, create new proxy
    output_url = nersc.lookup_url(output_path)
    reader = NERSCReader(output_url)
    return NERSCDataObject(reader, output_url)
