from __future__ import print_function
import datetime

import requests

from gaia.util import GaiaException, MissingParameterError


class NERSCInterface(object):
    """An internal class that provides a client interface to a NERSC HPC machine

    Uses the NEWT web service API at NERSC.
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
            raise RunTimeError('NOT authenticated, response: {}'.format(r.text))

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

    def lookup_url(self, path, test=False):
        """Returns internal url for resource at specified path

        :param path: (string) NERSC path, relative to user's home directory
        :param test: (boolean) if True, raise exception if resource not found
        """

        gaia_url = 'nersc:/{}/{}.nersc'.format(self.home_directory, path)

        if test:
            # TODO
            pass

        return gaia_url
