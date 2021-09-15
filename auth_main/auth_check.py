#!/usr/bin/env python3
from .funct_tools import query_request, other_requests
from .logger import logging as log
#taken straight from centrify.dmc module
#https://github.com/centrify/dmc-python/blob/master/main.py

def sec_test(tenant, header, **ignored):
    log.info("Going to do a security test and verify that the connection can occur, if not, will drop")
    log.info("Testing the connection for tenant: {0}".format(tenant))
    check = other_requests("/Security/Whoami", tenant, header).parsed_json
    if check['success'] == False:
        log.error("Serious issue occurred, will not continue.")
        raise SystemExit(0)
    log.info("Tenant: {0}".format(check['Result']["TenantId"]))
    log.info("User: {0}".format(check['Result']["User"]))
    log.debug("UserUuid: {0}".format(check['Result']["UserUuid"]))
    log.info("Passed the test")