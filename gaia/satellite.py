#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc. and Epidemico Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
from osgeo import gdal
from gaia.geo.geo_inputs import RasterFileIO


def multi_band_merge(input_loc, output_loc):
    """
    Merge multiple TIF images into one multi-band image

    :param input_loc: List of TIF images to be merged
    :param output_loc: Merged multi-band TIF image
    :return: 
    """

    # Input asserts.
    assert len(input_loc) > 0

    # Read files.
    input_images = [RasterFileIO(uri=loc).read() for loc in input_loc]

    # Get band counts by image.
    input_band_counts = [img.RasterCount for img in input_images] 

    # Generate an output image.
    output_image = gdal.GetDriverByName('MEM').CreateCopy('', input_images[0], 0)
    
    # Merge bands into output image.
    for img in range(1, len(input_images)):
        for band in range(0, input_band_counts[img]):
            output_image.AddBand()
            output_image.GetRasterBand(output_image.RasterCount).WriteArray(input_images[img].GetRasterBand(band+1).ReadAsArray())
        
    # Write to output file.
    dest = gdal.GetDriverByName('GTiff').CreateCopy(output_loc, output_image, 0)
    del dest

    return



