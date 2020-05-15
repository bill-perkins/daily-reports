# process.py
#
import sys

import lclvars

from utils import *
from getentry import *
from parseentry import *

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """bring the contents of the given input file into a list,
       and return the list.
       filename: name of the file we're processing (daily.log)
       returns:  list of lines from given file
    """

    logcontent = []

    # open given filename, bring it in as a list:
    try:
        with open(filename, 'r') as inpfile:
            logcontent = inpfile.readlines()

    except FileNotFoundError as err:
        print('getContent():', str(err))
        sys.exit(0)

    except PermissionError as err:
        print('getContent():', str(err))
        sys.exit(0)

    return deque(logcontent)

# ----------------------------------------------------------------------------
# getEntry(inpdata)
# ----------------------------------------------------------------------------
def getEntry(inpdata):
    """ Bring in lines from current index, until we see '----'.
            inpdata:  list of lines from getContent()
            index:    line # we start processing at
            maxindex: last line index of inpdata

        returns:
            outlist:  list of lines in this entry
    """

    outlist = []
    while True:
        try:
            line = inpdata.popleft()
        except IndexError as err:
            return None

        if line[0:4] == '----':
            break;

        outlist.append(line)

    return outlist

# ----------------------------------------------------------------------------
# process(logfile)
# ----------------------------------------------------------------------------
def process(logfile):
    """ Take a given log file and return the system name,
        along with all the dated entries in a dictionary
    """

    print('processing:', logfile)

    ix = 0              # current index into inp_file
    cur_syskey = ''     # current system name
    inp_entry = []      # create local entry list
    out_entry = []      # create local entry list
    datedEntries = {}   # dictionary as datestamp: logEntries
    curSystime = ''     # system time of this entry

    inp_file = getContent(logfile)  # bring file into inp_file
    inp_max  = len(inp_file)        # lines in file
    if inp_max == 0:
        print('process(): empty file', logfile)
        return None, None

    # get the hostname out of the log file:
    for line in inp_file:
        if 'corp.local' in line and ' ping ' not in line:
            cur_syskey = line.split(':')[0]
            break;

    if cur_syskey == '':
        print("can't find system hostname in", logfile)
        print('...skipping...')
        print()
        return None, None

    lclvars.curSysname = cur_syskey

#    while ix < inp_max:
    while True:

        # declare logEntries here so we always have a fresh one:
        logEntries = {}  # dictionary with log parameter as key, value as value

        # read in a full log entry:
#        ix, inp_entry = getEntry(inp_file, ix, inp_max)
        inp_entry = getEntry(inp_file)
        if inp_entry == None:
            break;

        # parse inp_entry into a list of key:value pairs in out_entry
        out_entry = parseEntry(inp_entry)

        # put the key:value pairs into logEntries;
        # handle Datestring, Datestamp, and Sysname special:
        dateKey = ''    # fresh dateKey
        for x in out_entry:
            thisKey = x[0]
            thisVal = x[1:]

            if 'Datestamp' in thisKey:
                dateKey = thisVal[0]
            elif 'Systime' in thisKey:
                curSystime = thisKey
            elif 'Sysname' in thisKey:
                if thisVal[0] != lclvars.curSysname:
                    print("Foreign system name in input file: '" + thisVal[0] + "'")
                    print("thisVal[0] =", thisVal[0], "lclvars.curSysname =", lclvars.curSysname)
                    sys.exit(1)
            elif 'Datetime' in thisKey:
                logEntries[thisKey] = thisVal
            else:
                logEntries[thisKey] = thisVal

        # create datedEntries using the datestamp for its keys:
        datedEntries[dateKey] = logEntries

    return lclvars.curSysname, datedEntries

# EOF:
