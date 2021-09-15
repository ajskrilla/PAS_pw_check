import requests
import json
import traceback
from .logger import logging as log

# AT's Work
def boolize(v):
    return {
        "TRUE": True,
        "FALSE": False,
    }.get(v.upper() if hasattr(v,"upper") else "", v)
def sanitizedict(d):
    return {k:boolize(v) for k,v in d.items() if v!= ""}
# AT's Work
def rem_null(args):
    return dict((k, v) for k, v in args.items() if v != None)
#RedRock Query
# Make Header as an argument for cache as well as tenant
class query_request:
    def __init__(self, sql, url, header, Debug=False):
        q_url = "{0}/Redrock/Query".format(url)
        log.info("Starting Query Request....")
        log.info("Query is: {0}".format(sql))
        try:
            self.query_request = requests.post(url=q_url, headers=header, json={"Script": sql}).json()
        except Exception as e:
            log.error("Internal error occurred. Please note it failed on a Query request.")
            log.error(traceback.print_exc(e))
        self.jsonlist = json.dumps(self.query_request)
        self.parsed_json = (json.loads(self.jsonlist))
        if self.parsed_json['success'] == False:
            log.error("Issue with Query. Dump is: {0}".format(self.jsonlist))
        log.debug("JSON dump of Query is : {0}".format(self.jsonlist))
        log.info("Finished Query")
        if Debug == True:
            print(json.dumps(self.parsed_json, indent=4, sort_keys=True))
#for other requests
# Make Header as an argument for cache as well as tenant
class other_requests:
    def __init__(self, Call, url, header, Debug=False, **kwargs):
        r_call = '{0}{1}'.format(url, Call)
        self.kwargs = kwargs
        self.__dict__.update(**self.kwargs)
        try:
            log.info("Starting request...")
            log.info("Endpoint is: {0}".format(Call))     
            self.other_requests = requests.post(url=r_call, headers=header, json=self.kwargs).json()
        except Exception as e:
            log.error("Internal error occurred. Please note it failed on an other request")
            log.error(traceback.print_exc(e))
        self.jsonlist = json.dumps(self.other_requests)
        self.parsed_json = (json.loads(self.jsonlist))
        if self.parsed_json['success'] == False:
            log.error("Issue with other request. Dump is: {0}".format(self.jsonlist))
        log.debug("JSON dump of request is : {0}".format(self.jsonlist))
        log.info("Finished request")
        if Debug == True:
            print(json.dumps(self.parsed_json, indent=4, sort_keys=True))
#make complicated request so that it trasfers complicated objects. This will allow to arrayed dicts and whatnot
