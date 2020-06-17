"""
A script that filters and sorts the provided input_log.txt file based on command line parameters.  The filter
should be able to filter the requested log lines from the file based on either log level [DEBUG, INFO, WARNING], date,
or origin module.  The output should be sorted in ascending order of time, module, or log_level.  The final output
should be placed in a file called "outlog.txt"

EXAMPLE:
DEBUG - root - Preparing to Launch Script
2016-06-07 01:01:12,465 - INFO - helpers.highwinds - Authorizing...
2016-06-07 01:01:08,399 - WARNING - buildsystem - Running attrib -R C:\cygwin64\home\Build\download\*.* /S

The first line has a log level of DEBUG, the second is INFO, and the last is WARNING.
The second two lines have a timestamp of yyyy-mm-dd hh:mm:ss,fff
The origin module of the first line is root, the second is from helpers.highwinds, and the last is from buildsystem

A request to output lines sorted by date would show:

    2016-06-07 01:01:08,399 - WARNING - buildsystem - Running attrib -R C:\cygwin64\home\Build\download\*.* /S
    2016-06-07 01:01:12,465 - INFO - helpers.highwinds - Authorizing...

A request to filter lines by log level = DEBUG would only show:

    DEBUG - root - Preparing to Launch Script

USE CASE 1:
    Retrieve all lines that are log level WARNING from buildsystem module sorted by time

        2016-06-06 01:01:08,399 - WARNING - buildsystem - Running attrib -R C:\cygwin64\home\Build\download\*.* /S
        2016-06-07 02:04:08,870 - WARNING - buildsystem - Running attrib -R C:\cygwin64\home\Build\download\*.* /S
        2016-06-08 05:17:10,420 - WARNING - buildsystem - Running attrib -R C:\cygwin64\home\Build\download\*.* /S

USE CASE 2:
    Retrieve all lines from module root sorted by log level

        DEBUG - root - Initializing Branch Specific Settings
        2016-05-04 10:05:09,800 - DEBUG - root - Preparing to Launch Script
        INFO - root - Preparing to Launch Script

USE CASE 3:
    Retrieve all lines from module root

        2016-05-04 10:05:09,800 - DEBUG - root - Preparing to Launch Script
        INFO - root - Preparing to Launch Script
        DEBUG - root - Initializing Branch Specific Settings
        2016-02-03 12:17:19,256 - DEBUG - root - Preparing to Launch Script

Test the script using the following command format:
    python log_filter.py input_file [--log_level {DEBUG,INFO,WARN}] [--module MODULE]
                   [--date DATE] [--sort_value {time,log_level,module}]
"""

'''
    @author  Spencer Jamieson
    @version 1.0
    @since   2020-14-2020
'''

import argparse
import os
import pandas as pd
import sys
from dateutil.parser import parse

# Filter all_logs_containing_logs from all_lines. 
# Example: "[timeout: 5 workingDir: C:\cygwin64\home\Build\download]" I figured this isn't a proper log.
def filter_for_logs(all_lines_containing_logs_input):
    log_levels_found = []
    for item in all_lines_containing_logs_input:
        # I decided to use " - " since it appears as a specific identifier of log lines. 
        items = item.split(" - ")
        if(len(items) > 2):
            log_levels_found.append(items)
    return log_levels_found

def handle_arguments(arg_input, arg_parameter, all_logs_to_write_to_file):
    if arg_input == "--log_level":
        return find_log_level(arg_parameter)
    elif arg_input == "--module":
        return find_module(arg_parameter)
    elif arg_input == "--date":
        return find_date(arg_parameter) 
    elif arg_input == "--sort_value":
        return handle_sort_value(arg_parameter.lower())
    else:
        print("DEBUG: Warning")
        return
    
#Used to check if string contains TimeStamp
def contains_date(string, fuzzy=False):
    try: 
        parse(string, fuzzy=fuzzy)
        return True
    except ValueError:
        return False

def find_date(arg_parameter):
    list_to_return = []
    if check_if_search_list_defined():
        for log in all_lines_containing_logs:
            if arg_parameter in log[0] and contains_date(log[0]):
                list_to_return.append(log)
    else:
        for log in all_logs_to_write_to_file:
            if arg_parameter in log[0] and contains_date(log[0]):
                list_to_return.append(log)
    return list_to_return  

def find_log_level(arg_parameter):
    list_to_return = []
    if check_if_search_list_defined():
        for log in all_lines_containing_logs:
            if arg_parameter in log[1]:
                list_to_return.append(log)
    else:
        for log in all_logs_to_write_to_file:
            if arg_parameter in log[1]:
                list_to_return.append(log)

    return list_to_return

def find_module(arg_parameter):
    list_to_return = []

    if check_if_search_list_defined():
        for log in all_lines_containing_logs:
            if arg_parameter in log[2]:
                list_to_return.append(log)
    else:
        for log in all_logs_to_write_to_file:
            if arg_parameter in log[2]:
                list_to_return.append(log)

    return list_to_return

def handle_sort_value(value_input):
    if value_input == "time":
        sorted_list = sorted((log for log in all_logs_to_write_to_file), key=lambda log: (log[0]), reverse=False)
        return sorted_list
    elif value_input == "log_level":
        sorted_list = sorted((log for log in all_logs_to_write_to_file), key=lambda log: (log[1]), reverse=False)
        return sorted_list
    elif value_input == "module":
        sorted_list = sorted((log for log in all_logs_to_write_to_file), key=lambda log: (log[2]), reverse=False)
        return sorted_list

def write_to_file(file_name):
    with open(file_name, 'w') as f:
        #remove dummy elements if any before writing back to the document
        for item in all_logs_to_write_to_file:
            if item[0] == "_":
                item.pop(0)

        for item in all_logs_to_write_to_file:
            f.write("%s\n" % item)

#Once we have an existing "logs_to_be_outputed_to_console" list elements to compare to, we won't change it
def check_if_search_list_defined():
    global is_search_list_defined
    try:
        return is_search_list_defined
    except NameError:
        is_search_list_defined = False
        return True

if __name__ == "__main__":
    currentDirectorOfLogFile = os.getcwd() + "\\" + str(sys.argv[1])
    
    #A list of all lines, including spaces
    all_lines = []

    #A list of all logs, to contain some form of DEBUG, INFO, or WARN, and also modules, with or without dates/timestamps
    all_lines_containing_logs = []

    #A list of all logs to write to file
    all_logs_to_write_to_file = []

    #Gather all logs/lines within the text document
    with open(currentDirectorOfLogFile) as f:
        for line in f:
            all_lines.append(line)

    # Filter all_logs_containing_logs from all_lines. 
    # Example: "[timeout: 5 workingDir: C:\cygwin64\home\Build\download]" I figured this isn't a proper log.
    all_lines_containing_logs = filter_for_logs(all_lines)

    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="(str)file_name")
    parser.add_argument("--log_level", help="(str){DEBUG,INFO,WARN}")
    parser.add_argument("--module", help="(str)MODULE")
    parser.add_argument("--date", help="(str)DATE")
    parser.add_argument("--sort_value", help="(str){time,log_level,module}")
    args = parser.parse_args()

    #number of args inputed into the console, minus the two initial parameters(Python filename and TextFile name)
    remaining_console_args = sys.argv[2:]

    #Insert temporary dummy element into lists without timestamps to make sorting easier
    for item in all_lines_containing_logs:
        if not(contains_date(item[0])):
            item.insert(0,"_")

    #Feed each optional args and associated parameters into a method to handle the priority of execution
    for i,k in zip(remaining_console_args[0::2], remaining_console_args[1::2]):
        all_logs_to_write_to_file = handle_arguments(i, k, all_logs_to_write_to_file)
    write_to_file("outlog.txt")