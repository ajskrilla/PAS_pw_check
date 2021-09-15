import csv
import os
import json
from datetime import datetime
from .logger import logging as log
from .logger import f_check
from cachetools import TTLCache
import getpass
import requests
# Check for DMC and if not installed, let user know and continue
try:
    from dmc import gettoken
except ImportError:
    log.warning("Please use pip install centrify.dmc to use DMC auth")

# File classes

f = f_check()
class rep_data:
    # Holds all info of success failures and does a check on them at the end
	def __init__(self):
		self._num_of_succ = 0
		self._num_of_fail = 0
		self.f_list = []
		self.s_list = []
		self.f_dict = {}
		self.s_dict = {}

	def check(self):
		if self._num_of_fail > 0:
			log.info("Succeeded on {0} actions, but failed on {1} actions, out of a total of {2} actions".format(self._num_of_succ, self._num_of_fail, (self._num_of_succ + self._num_of_fail)))
			for failures in self.f_list:
				log.error("Failed on object: {0} for reason: {1}".format(failures['Name'], failures['Message']))
			for successes in self.s_list:
				log.info("Successful object name: {0}".format(sorted(successes['Name'])))
		else:
			log.info("Successfully did {0} actions".format(self._num_of_succ))

# Write failed info to dict

def write_rep_data(prefix, fail_dict=None):
    curr_dir = os.getcwd()
    fail_dir = os.path.join(curr_dir, + prefix + 'Error_report ' + str(datetime.now()) + '.csv')
    if fail_dict != None:
        try:
            with open (fail_dir, 'w') as f:
                log.info("Writing failed report to current dir if there is one. Saved as: {0}".format(fail_dir))
                writer= csv.DictWriter(f, fieldnames=fail_dict[0].keys(), delimiter=',')
                writer.writeheader()
                writer.writerows(fail_dict)
        except IndexError:
            log.info("No errors to write.")
            pass

# For the OAUTH process

class auth:
    def __init__(self, **kwargs):
        if kwargs['auth'].upper() == 'DMC':
            log.info('Setting auth headers for DMC......')
            self._headers = {}
            self._headers["X-CENTRIFY-NATIVE-CLIENT"] = 'true'
            self._headers['X-CFY-SRC' ]= 'python'
            try:
                self._headers['Authorization']  = 'Bearer {scope}'.format(**kwargs)
            except KeyError:
                log.error('Issue with getting DMC scope')
                raise Exception
        elif kwargs['auth'].upper() == 'OAUTH':
            log.info("Going to authenticate Oauth account: {client_id}".format(**kwargs['body'])) 
            # Handle the fact that client_secret can be added to the config file and skip the ask
            self.json_d = json.dumps(kwargs['body'])
            self.update = json.loads(self.json_d)
            self.update['scope'] = kwargs['scope']
            if 'client_secret' not in kwargs['body']: 
                log.warning("Password Not Saved, Please provide password of Oauth Account or save PW")
                self._pw = getpass.getpass("Please provide Password for Oauth account: {client_id}\n".format(**kwargs['body']))
                self.json_d = json.dumps(kwargs['body'])
                self.update = json.loads(self.json_d)
                self.update['client_secret'] = self._pw
            else:
                self._rheaders = {}
                self._rheaders['X-CENTRIFY-NATIVE-CLIENT'] = 'true'
                self._rheaders['Content-Type'] = 'application/x-www-form-urlencoded'
                log.info('Oauth URL of app is: {tenant}/Oauth2/Token/{appid}'.format(**kwargs, **kwargs['body'])) 
                log.info('Oauth token request Headers are: {}'.format(self._rheaders)) 
                try:
                    log.info('Setting auth headers for OAUTH......')
                    req = requests.post(url='{tenant}/Oauth2/Token/{appid}'.format(**kwargs, **kwargs['body']), headers= self._rheaders, data= self.update).json()
                except:
                    log.error("Issue getting token")
                    log.error("Response: {0}".format(json.dumps(req)))
                self._headers = {}
                self._headers["Authorization"] = "Bearer {access_token}".format(**req)
                self._headers["X-CENTRIFY-NATIVE-CLIENT"] = 'true'
        else:
            log.error("Not valid auth type. Please fix")
    @property
    def headers(self):
        return self._headers

# Cache class that utilizes the auth class

class Cache:
    def __init__(self, **kwargs):
        # Make TTL setting to grab in conf file next to debug
        self._cache = TTLCache(maxsize=10, ttl=600)
        try:
            log.info("Building the cache..")
            self._cache['header'] = auth(**kwargs).headers
            self._cache['tenant'] = kwargs['tenant']
        except:
            log.error("Failed to build cache")
            log.error("Cannot continue. Exiting")
            raise SystemExit(0)
    @property
    def ten_info(self):
        return self._cache
    @property
    def dump(self):
        log.info("Dumping the cache.")
        self._cache.clear()