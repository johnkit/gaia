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
import json
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

    # Read crop geometry file
    with open(args.geometry_path) as f:
        content = f.read()
        geometry = json.loads(content)

    # Generate cropped output
    gaia.preprocess.crop(input_object, geometry, output_path)

    # No errors
    sys.exit(0)