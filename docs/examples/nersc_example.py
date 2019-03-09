"""
Example program to demonstrate gaia object proxy to NERSC file
"""

import argparse
import getpass

import geojson

import gaia
from gaia.io import NERSCInterface

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NERSC object example')

    # Add session id either as string or file to read
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--newt_sessionid', '-n', help='newt session id')
    group.add_argument('--id_filename', '-i', help='filename containing newt session id')

    args = parser.parse_args()
    # print(args)

    newt_sessionid = None
    if args.newt_sessionid:
        newt_sessionid = args.newt_sessionid
    elif args.id_filename:
        with open(args.id_filename) as f:
            newt_sessionid = f.read().strip()

    nersc_client = NERSCInterface.get_instance()

    # Check NEWT session id if passed in; otherwise login
    if newt_sessionid:
        print('Checking authentication')
        nersc_client.initialize(newt_sessionid)
    else:
        print('Log into NERSC')
        username = input('Enter NERSC username: ')
        password = getpass.getpass(prompt='Enter password: ')
        OTP = input('Enter one time password (MFA): ')
        nersc_client.initialize(username=username, password=password, OTP=OTP)


    # Create NERSCObject instance
    # (The SFBay tif file has been manually uploaded to cori)
    cori_path = 'project/data/TC_NG_SFBay_US_Geo.tif'
    sfbay_url = nersc_client.lookup_url(cori_path)
    print('sfbay_url: {}'.format(sfbay_url))

    sfbay_object = gaia.create(sfbay_url)
    print('sfbay_object: {}'.format(sfbay_object))

    metadata = sfbay_object.get_metadata()
    print('metadata: {}'.format(metadata))

    # Setup crop geometry from image bounds
    bounds = metadata.get('bounds',{}).get('coordinates')[0]
    assert bounds, 'Dataset bounds missing'
    # print(bounds)

    # Compute center coordinates
    x = (bounds[0][0] + bounds[2][0]) / 2.0
    y = (bounds[0][1] + bounds[2][1]) / 2.0

    # Use a percentage of height & width
    dx = 0.1 * (bounds[2][0] - bounds[0][0])
    dy = 0.1 * (bounds[2][1] - bounds[0][1])

    x += dx
    y -= dy
    poly = [
        [x,y], [x+dx,y+dy], [x-dx,y+dy], [x-dx,y-dy], [x+dx,y-dy]
    ]

    # Pass rectangle in as a LIST, to used same format as resgeodata
    crop_geom = geojson.Polygon([poly])
    print('crop geometry: {}'.format(crop_geom))

    import gaia.preprocess
    cropped_dataset = gaia.preprocess.crop(
        sfbay_object, crop_geom, output_path='project/data/sfbay_crop.tif')

    print('finis')

    ### Freelancing
    # import requests

    # # Try ls of project/data directory
    # print('List files in project/data')
    # path = '{}/project/data'.format(home_directory)
    # url = '{}/file/cori{}/'.format(nersc_client.nersc_url, path)
    # r = requests.get(url, cookies=cookies)
    # r.raise_for_status()
    # js = r.json()
    # print(js)

    # print('List SFBay file')
    # path = '{}/project/data/TC_NG_SFBay_US_Geo.tif'.format(home_directory)
    # url = '{}/file/cori{}/'.format(nersc_client.nersc_url, path)
    # r = requests.get(url, cookies=cookies)
    # r.raise_for_status()
    # js = r.json()
    # print(js)
