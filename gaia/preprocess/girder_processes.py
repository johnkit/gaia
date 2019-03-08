from __future__ import absolute_import, division, print_function
from builtins import (
    bytes, str, open, super, range, zip, round, input, int, pow, object
)
import sys
from urllib.parse import urlencode

import collections
import json

import gaia.types
import gaia.validators as validators
from gaia.util import GaiaException
from gaia.gaia_data import GaiaDataObject
from gaia.girder_data import GirderDataObject
from gaia.process_registry import register_process


def validate_girder(v):
    """
    Verify that inputs are all girder objects
    """
    def validator(inputs=[], args={}):
        # First object must be GirderDataObject
        if (type(inputs[0]) is not GirderDataObject):
            raise GaiaException('girder process requires GirderDataObject')

        # Second object must have vector geometry
        # and, for now, be on the local filesystem
        geom_input = inputs[1]
        if (isinstance(geom_input, GaiaDataObject)):
            if geom_input.is_remote():
                raise GaiaException('crop geometry from remote object not supported')

            elif geom_input.get_datatype() != gaia.types.VECTOR:
                template = """girder process cannot use datatype \"{}\"" \
                    for crop geometry"""
                raise GaiaException(template.format(geom_input.get_datatype()))
        # Otherwise call up the chain to let parent do common validation
        return v(inputs, args)

    return validator


@register_process('crop')
@validate_girder
def compute_girder_crop(inputs=[], args_dict={}):
    """
    Runs the subset computation on girder
    """
    datasets = inputs[0]
    if isinstance(inputs[1], GaiaDataObject):
        geometry = inputs[1].get_data()
    else:
        geometry = inputs[1]
    # print('datasets: ', datasets)
    # print('geometry:', geometry)
    # print('args_dict:', args_dict)

    # if not isinstance(input, collections.Iterable):
    #     datasets = [datasets]

    # Current support is single dataset

    filename = args_dict.get('name', 'crop_output.tif')
    # print(filename)

    from gaia.io.girder_interface import GirderInterface
    gc = GirderInterface._get_girder_client()
    results_folder_id = GirderInterface._get_default_folder_id()

    # Check for existing file (and delete)
    result = gc.listItem(results_folder_id, name=filename)
    # print(result)
    for item in result:
        item_path = 'item/{}'.format(item['_id'])
        print('Deleting existing (item {})'.format(filename, item_path))
        del_result = gc.delete(item_path)
        print(del_result)

    # Run the clip operation
    path = 'raster/clip'
    params = {
        'itemId': datasets.resource_id,
        'geometry': json.dumps(geometry),
        'name': filename,
        'folderId': results_folder_id
    }
    job = gc.get(path, parameters=params)
    # print()
    # print(job)

    import time
    path = 'job/{}'.format(job['_id'])
    status = job['status']
    for i in range(50):
        if status >= 3:
            break
        # (Using sys.stdout to skip newline at end)
        sys.stdout.write(
            '{:2d} Checking job {} status... '.format(i+1, job['_id']))
        time.sleep(1.0)
        job = gc.get(path)
        status = job['status']
        print(status)

    # Get item id of (new) output file
    result = gc.listItem(results_folder_id, name=filename)
    cropped_item = next(result)
    # print(cropped_item)

    outputDataObject = GirderDataObject(None, 'item', cropped_item['_id'])
    return outputDataObject
