from __future__ import print_function
import json
import os

import geojson
import requests

from gaia.util import GaiaException


class NERSCInterface(object):
    """An internal class that provides a client interface to a NERSC HPC machine

    Uses the NEWT web service API at NERSC, along with python scripts
    on cori and known paths.

    This class must be used as a singleton.
    """

    instance = None  # singleton

    def __init__(self):
        """Applies crude singleton pattern (raise exception if called twice)
        """
        if NERSCInterface.instance:
            msg = """NERSCInterface already exists \
            -- use get_instance() class method"""
            raise GaiaException(msg)

        NERSCInterface.instance = self

        self.home_directory = None
        self.nersc_url = 'https://newt.nersc.gov/newt'
        self.newt_sessionid = None

    @classmethod
    def get_instance(cls):
        """Returns singleton instance, creating if needed.
        """
        if cls.instance is None:
            cls.instance = cls()

        return cls.instance

    @classmethod
    def is_initialized(cls):
        if cls.instance is None:
            return False

        if cls.get_instance().newt_sessionid is None:
            return False

        # (else)
        return True

    def get_session_id(self, username, password, OTP):
        """Requests NEWT session id with input credentials"""
        credentials = {
            'username': username,
            'password': password + str(OTP)
        }
        url = '{}/login/'.format(self.nersc_url)
        r = requests.post(url, data=credentials)
        r.raise_for_status()

        js = r.json()
        print(js)
        if js.get('auth'):
            session_id = js.get('newt_sessionid')
            return session_id
        else:
            raise GaiaException('NOT authenticated, response: {}'.format(r.text))

    def get_session_status(self, newt_sessionid=None):
        """Requests current authentication status and number of seconds

        """
        cookies = dict(newt_sessionid=newt_sessionid)
        url = '{}/login/'.format(self.nersc_url)
        r = requests.post(url, cookies=cookies)
        r.raise_for_status()

        js = r.json()
        return js

    def initialize(self, newt_sessionid=None, username=None, password=None, OTP=None):
        """Connect to NERSC NEWT server and authenticate with input credentials

        :param newt_sessionid: A NERSC session id, the preferred input
        :param username: The NERSC account user name.
        :param password: The NERSC account password
        :param OTP: The NERSC one-time password (MFA).
        """
        if self.__class__.is_initialized():
            msg = """NERSCInterface already initialized -- \
                cannot initialize twice"""
            raise GaiaException(msg)

        if newt_sessionid:
            status = self.get_session_status(newt_sessionid)
            if not status.get('auth'):
                print('Session id not authenticated - either expired or invalid')
                return None
            # (else)
            self.newt_sessionid = newt_sessionid

        # (else)
        # print('Log into NERSC')
        # username = input('Enter NERSC username: ')
        # password = getpass.getpass(prompt='Enter password: ')
        # OTP = input('Enter one time password (MFA): ')
        else:
            self.newt_sessionid = self.get_session_id(
                username, password, OTP)

        print('NEWT session id {}'.format(newt_sessionid))

        print('Getting home directory')
        cookies = dict(newt_sessionid=self.newt_sessionid)
        machine = 'cori'
        url = '{}/command/{}'.format(self.nersc_url, machine)
        data = {
            'executable': 'pwd',
            'loginenv': 'true'
        }
        r = requests.post(url, cookies=cookies, data=data)
        r.raise_for_status()
        self.home_directory = r.json().get('output')
        print('Home directory: {}'.format(self.home_directory))

        return True

    def load_metadata(self, nersc_path):
        """Run command (script) on cori to get metadata.

        @param nersc_path: *relative* path to data file
        """
        global_path = os.path.join(self.home_directory, nersc_path)
        commands = [
            'module load python/3.6-anaconda-4.4',
            'source activate py3',
            'cd project/git/gaia',
            'PYTHONPATH=. python nersc/getmetadata.py {}'.format(global_path)
        ]
        exe = ' &&' .join(commands)
        data = {
            'executable': exe,
            'loginenv': 'true'
        }
        url = '{}/command/cori'.format(self.nersc_url)
        cookies = dict(newt_sessionid=self.newt_sessionid)
        print('requesting metadata')
        r = requests.post(url, data=data, cookies=cookies)
        r.raise_for_status()
        js = r.json()
        if js.get('status') == 'OK':
            output = js.get('output')
            metadata = json.loads(output)
            return metadata
        else:
            raise GaiaException('ERROR: {}'.format(js.get('error')))

    def compute_crop(self, input_path, geometry, output_path):
        """Run commands (scripts) on cori to compute cropped dataset.

        """
        # First upload cropping geometry to hard-coded location
        print('Uploading crop geometry')
        geometry_filename = 'crop_geometry.geojson'
        geom_path = os.path.join(self.home_directory, 'project', 'data')
        url = '{}/file/cori/{}'.format(self.nersc_url, geom_path)
        cookies = dict(newt_sessionid=self.newt_sessionid)
        files = dict(file=(geometry_filename, json.dumps(geometry)))
        r = requests.post(url, files=files, cookies=cookies)
        r.raise_for_status()

        geometry_path = os.path.join(self.home_directory, 'project', 'data', geometry_filename)

        # Expect output_path to be relative to home dir
        if not output_path.startswith('/'):
            output_path = os.path.join(self.home_directory, output_path)

        # Run script to compute the crop
        args = ' '.join([input_path, geometry_path, output_path])
        commands = [
            'module load python/3.6-anaconda-4.4',
            'source activate py3',
            'cd project/git/gaia',
            'PYTHONPATH=. python nersc/crop.py {}'.format(args)
        ]
        exe = ' &&' .join(commands)
        data = {
            'executable': exe,
            'loginenv': 'true'
        }
        url = '{}/command/cori'.format(self.nersc_url)
        print('Requesting crop')
        r = requests.post(url, data=data, cookies=cookies)
        r.raise_for_status()
        js = r.json()
        print(js)
        if js.get('status') != 'OK':
            raise GaiaException('ERROR: {}'.format(js.get('error')))

    def lookup_url(self, path, test=False):
        """Returns internal url for resource at specified path

        :param path: (string) NERSC path, relative to user's home directory
        :param test: (boolean) if True, raise exception if resource not found
        """

        gaia_url = 'nersc://{}/{}.nersc'.format(self.home_directory, path)

        if test:
            # TODO
            pass

        return gaia_url
