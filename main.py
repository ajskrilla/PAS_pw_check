import csv
import os
import errno
import time
from datetime import datetime
from auth_main.logger import f_check
from auth_main.logger import logging as log
from auth_main.utility import Cache, rep_data
from auth_main.funct_tools import query_request, other_requests
from auth_main.auth_check import sec_test

# Create the object for the file
f = f_check()

# Build cache
c = Cache(**f.loaded['tenants'][0])

# Security test
sec_test(**c.ten_info)

# Function to do the data
def inner_get_pw_info(tenant, header, **ignored):
    log.info("Building the data set and timing this process.")
    # Timer
    log.info(":::Start Timer::: {0}".format(datetime.now()))
    start_time = time.time()
    pRes = query_request("SELECT VaultAccount.ID, VaultAccount.IsManaged, VaultAccount.UserDisplayName \
        FROM VaultAccount", tenant, header).parsed_json["Result"]["Results"]
    for raw in pRes:
        pw_info = raw['Row']
        if not pw_info['IsManaged']:
            pw_ret =  other_requests('/ServerManage/CheckoutPassword', tenant, header, ID=pw_info['ID']).parsed_json
            if pw_ret['success'] == False:
                log.error("Issue with account: {UserDisplayName}".format(**pw_info))
            else:
                log.info("got PW for account: {UserDisplayName}".format(**pw_info))
                pw_info['Password length'] = len(pw_ret['Result']['Password'])
                log.info("Checking PW now")
                if pw_ret['Result']['COID'] != None:
                    pw_c_in = other_requests('/ServerManage/CheckinPassword', tenant, header, ID=pw_ret['Result']['COID']).parsed_json
                    if pw_c_in['success'] == False:
                        log.error("Issue with check in with account: {UserDisplayName}".format(**pw_info))
                        continue
        del pw_info['ID']
        del pw_info['IsManaged']
        del pw_info['_TableName']
        yield pw_info
    log.info(":::End Timer::: {0}".format(datetime.now()))
    log.info("--- Took {0} Minutes to get Pws---".format(((time.time() - start_time)/60)))

# Return the list 
def get_pw_info(c):
    return list(inner_get_pw_info(**c.ten_info))

# Write csv file
def write_to_csv(wanted):
    # Check to see the OS
    time = str(datetime.now())
    if os.name == "posix":
        path = os.path.join(os.path.join(os.path.expanduser('~')), 'report', 'pw_report_' + time + '.csv') 
    elif os.name == "nt":
        path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'report', 'pw_report_' + time + '.csv')
    if not os.path.exists(os.path.dirname(path)):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(path, 'w') as f:
        writer= csv.DictWriter(f, fieldnames=wanted[0].keys(), delimiter=',')
        writer.writeheader()
        writer.writerows(wanted)
        log.info("Report Saved to {0}".format(path))

write_to_csv(get_pw_info(c))