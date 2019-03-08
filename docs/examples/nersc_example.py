"""
Example program to demonstrate gaia object proxy to NERSC file
"""

import argparse
import getpass

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

    # if newt_sessionid:
    #     print('Checking session id {}'.format(newt_sessionid))
    #     cookies = dict(newt_sessionid=newt_sessionid)
    #     status = nersc_client.get_session_status(newt_sessionid)
    #     print(status)
    # else:
    #     print('Log into NERSC')
    #     username = input('Enter NERSC username: ')
    #     password = getpass.getpass(prompt='Enter password: ')
    #     OTP = input('Enter one time password (MFA): ')

    #     newt_sessionid = nersc_client.get_session_id(username, password, OTP)
    #     print('NEWT session id {}'.format(newt_sessionid))

        # filename = 'newt_sessionid.txt'
        # with open(filename, 'w') as f:
        #     f.write(newt_sessionid)
        #     print('Wrote {}'.format(filename))

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
    sfbay_url = nersc_client.lookup_url('project/data/TC_NG_SFBay_US_Geo.tif')
    print('sfbay_url: {}'.format(sfbay_url))


    ### Freelancing
    import requests

    # Try running python script
    commands = [
        'module load python/3.6-anaconda-4.4',
        'source activate py3',
        'cd project/git/gaia',
        'python nersc/getmetadata.py {}'.format('todo')
    ]
    exe = ' &&' .join(commands)
    data = {
        'executable': exe,
        'loginenv': 'true'
    }
    url = '{}/command/cori'.format(nersc_client.nersc_url)
    cookies = dict(newt_sessionid=nersc_client.newt_sessionid)
    print('requestiong metadata')
    r = requests.post(url, data=data, cookies=cookies)
    r.raise_for_status()
    js = r.json()
    print(js)

    import sys
    sys.exit()

    # Get home directory

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

    sfbay_object = gaia.create(sfbay_url)
    print('sfbay_object: {}'.format(sfbay_object))

    metadata = sfbay_url.get_metadata()
    print('metadata: {}'.format(metadata))

    print('finis')
