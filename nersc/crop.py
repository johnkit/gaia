"""
Script to run on NERSC machines for gaia preprocessing.
This is for basic demonstration of remote operations.

Example invocation (on john's account on cori):
    > module load python/3.6-anaconda-4.4'
    > source activate py3
    > cd project/git/gaia
    > python nersc/crop.py <path-to-input-file> <path-to-geometry-file> <path-to-output-file>
"""

import argparse
import sys

import gaia
import gaia.preprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_path', help='path to input data file')
    parser.add_argument('geometry_path', help='path to geometry file')
    parser.add_argument('output_path', help='path to output data file')

    args = parser.parse_args()

    # Create input object
    input_object = gaia.create(args.input_path)
    # print('input_object: {}'.format(input_object))

    # Create crop-geometry object
    geom_object = gaia.create(args.geometry_path)
    # geom_meta = geom_object.get_metadata()
    # print('geom_meta: {}'.format(geom_meta))

    # Generate cropped output
    output_object = gaia.preprocess.crop(input_object, geom_object)
    # print('output', output_object)
    gaia.save(output_object, args.output_path)
    print('Created {}'.format(args.output_path))

    # No errors
    sys.exit(0)
