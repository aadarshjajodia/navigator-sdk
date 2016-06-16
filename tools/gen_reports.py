#!/usr/bin/env python

from pyjavaproperties import Properties
from solr_stats import to_excel, NavSolrAnalyzer
import subprocess
import re
import os

USAGE = """
Usage: python gen_reports.py <config_file_path>

Sample config file:
# This is the URL of the client application
application_url=http://localhost

# Replace localhost:7187 with actual navigator URL
navigator_url=http://localhost:7187

# Minimum is version 7 for publishing metadata to Navigator
# Version 9 is minimum for typed custom property support
navigator_api_version=9

# Designator for client application
# This will be used as the meta class package and custom property namespace
namespace=example

# Navigator username and password
username=user
password=password

# File path for reports. Required to run gen_reports.py
optimizer_output_file=/tmp/opt_report.csv
sigma_output_file=/tmp/sig_report.csv
navigator_output_file=/tmp/nav_report.xlsx

# Query parameter for OperationExecution
principal=user

# Start time range for OperationExecution query
# Date formats can take form of 2012-07-06T9:23:43Z, NOW/DAY-5DAY, *
# For more information, https://cwiki.apache.org/confluence/display/solr/Working+with+Dates
start_time_min=2012-07-06T9:23:43Z

# Matches any date
start_time_max=*

# operation_execution_query will overwrite the above query parameters
#operation_execution_query=sourceType:HIVE AND type:operation_execution

# Parameter used to generate Navigator report. See solr_stats.py
client_name=foo

"""
URL_PATTERN = re.compile('http:\/\/(.*):([0-9]+)?\/*')
def gen_nav_analysis(config):
    matches = URL_PATTERN.match(config.get_property('navigator_url'))
    host = matches.group(1)
    port = matches.group(2)

    comp = NavSolrAnalyzer(config.get_property('client_name'), host, port,
    config.get_property('username'), config.get_property('password'))
    output_dir = config.get_property('output_directory')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    to_excel(comp, output_dir + "/nav.xlsx")

def query_extraction(config):
    subprocess.call('./query_extraction.sh ' + config.filepath, shell=True)

def gen_reports(config):
    gen_nav_analysis(config)
    query_extraction(config)

class Config(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = Properties()
        with open(filepath) as file:
            self.config.load(file)

    def get_property(self, key):
        return self.config[key]

if __name__=='__main__':
    import sys
    if len(sys.argv) < 2:
        sys.exit(USAGE)
    conf_file = sys.argv[1]

    config = Config(conf_file)

    gen_reports(config)