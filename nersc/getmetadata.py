"""
Script to run on NERSC machines for gaia preprocessing.
This is for basic demonstration of remote operations.

Example invocation (on john's account on cori):
    > module load python/3.6-anaconda-4.4'
    > source activate py3
    > cd project/git/gaia
    > python nersc/getmetadata.py <path-to-input-file>
"""

import argparse
import json

import gaia

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to data file')

    args = parser.parse_args()

    data_object = gaia.create(args.path)
    metadata = data_object.get_metadata()
    js = json.dumps(metadata)
    print(js)
