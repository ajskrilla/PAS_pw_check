import argparse
import os
import csv
from pathlib import Path
from auth_main.funct_tools import *
from auth_main.logger import logging as log
from auth_main.logger import f_check
from auth_main.utility import Cache
#https://developer.centrify.com/reference#post_servermanage-addaccounts
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a list of accounts from a CSV file. Examples are in data folder")
    parser.add_argument('-p','--Path', type=str, required=True, default=None, help= 'Path to the csv file. Point to csv in arg path and use forward slashes in the path if using windows. Required')
    args = parser.parse_args()

# Create the object for the file
f = f_check()

# Build cache
c = Cache(**f.loaded['tenants'][0])

# Security test
sec_test(**c.ten_info)

# Add account function
def add_accounts(tenant, header,**ignored):
    if args.Path != None:
        path = os.path.abspath(args.Path)
        csv_h_check(path, 'ParentEntityTypeOfAccount', 'User', 'Description', 'Password', 'DomainID')
        # UTF encode handling
        log.info("Path to the csv file to add accounts is: {0}".format(path))
        with open(path, 'r', encoding='utf-8-sig') as f:
            d_reader = csv.DictReader(f)
            data = [sanitizedict(dict(line)) for line in d_reader]
            log.info("Sanitizing and cleaning up dictionary. Data is: {0}".format(data))
            other_requests('/ServerManage/AddAccounts', tenant, header, Accounts=data, Debug=True)
add_accounts(**c.ten_info)