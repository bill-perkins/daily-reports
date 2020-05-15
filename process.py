# process.py
#
import sys
from collections import deque

import lclvars

from utils import *
from parseentry import *

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """bring the contents of the given input file into a list,
       and return the list.
       filename: name of the file we're processing (daily.log)
       returns:  deque of lines from given filename;
                exits program if file not found or permissions error.
    """

    logcontent = []

    # open given filename, bring it in as a list:
    try:
        with open(filename, 'r') as inpfile:
            logcontent = inpfile.readlines()

    except FileNotFoundError as err:
        print('getContent():', str(err))
        sys.exit(1)

    except PermissionError as err:
        print('getContent():', str(err))
        sys.exit(1)

    return deque(logcontent)

# ----------------------------------------------------------------------------
# getEntry(inpdata)
# ----------------------------------------------------------------------------
def getEntry(inpdata):
    """ Bring in lines from deque until we see '----'.
            inpdata:  deque of lines from getContent()

        returns:
            outlist:  list of lines in this entry
    """

    outlist = []

    line = inpdata.popleft()
    while line[0:4] != '----':
        outlist.append(line)
        try:
            line = inpdata.popleft()
        except IndexError as err:
            return None

    return outlist

# ----------------------------------------------------------------------------
# process(logfile)
# ----------------------------------------------------------------------------
def process(logfile):
    """ Take a given log file and return the system name,
        along with all the dated entries in a dictionary
    """

    print('processing log file:', logfile)

    cur_syskey = ''     # current system name
    inp_entry = []      # create local entry list
    out_entry = []      # create local entry list
    datedEntries = {}   # dictionary as datestamp: logEntries
    curSystime = ''     # system time of this entry

    inp_file = getContent(logfile)  # bring file into inp_file
    if len(inp_file) == 0:
        print('process(): empty file', logfile)
        return None, None

    # get the hostname out of the log file:
    for line in inp_file:
        if 'corp.local' in line and ' ping ' not in line:
            cur_syskey = line.split(':')[0]
            break;

    if cur_syskey == '':
        print("can't find hostname in", logfile)
        print('...skipping...')
        print()
        return None, None

    lclvars.curSysname = cur_syskey

    while True:
        # declare logEntries here so we always have a fresh one:
        logEntries = {}  # dictionary with log parameter as key, value as value

        # read in a full log entry:
        inp_entry = getEntry(inp_file)
        if inp_entry == None:
            break;

        # parse inp_entry into a list of key:value pairs in out_entry
        out_entry = parseEntry(inp_entry)

        # put the key:value pairs into logEntries;
        # handle Datestring, Datestamp, and Sysname special:
        dateKey = ''    # fresh dateKey
        for x in out_entry:
            key = x[0]
            val = x[1:]

            if 'Datestamp' in key:
                dateKey = val[0]
            elif 'Systime' in key:
                curSystime = key
            elif 'Sysname' in key:
                if val[0] != lclvars.curSysname:
                    print("Foreign system name in input file: '" + val[0] + "'")
                    print("val[0] =", val[0], "lclvars.curSysname =", lclvars.curSysname)
                    sys.exit(1)
            elif 'Datetime' in key:
                logEntries[key] = val
            else:
                logEntries[key] = val

        # create datedEntries using the datestamp for its keys:
        datedEntries[dateKey] = logEntries

    return lclvars.curSysname, datedEntries

# EOF:
