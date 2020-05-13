from utils import *
from getentry import *
from parseentry import *

# ----------------------------------------------------------------------------
# process()
# ----------------------------------------------------------------------------
def process(logfile, allSystems):
    """ Take a given log file and adds the data to the
        global allSystems dictionary.
    """

    global curSysname

    print('processing:', logfile)

    inp_file = getContent(logfile)      # get entire file into inp_file
    inp_max = len(inp_file)             # lines in file
    ix = 0                         # current index into inp_file
    cur_syskey = ''                     # current system name

    inp_entry = []                      # create local entry list
    out_entry = []                      # create local entry list

    datedEntries = {}                   # dictionary as datestamp: logEntries

    curSystime = ''                     # system time of this entry

    # get the hostname out of the log file:
    for line in inp_file:
        if 'corp.local' in line and ' ping ' not in line:
            cur_syskey = line.split(':')[0]
            break;

    if cur_syskey == '':
        print("can't find system hostname in", logfile)
        print('...skipping...')
        print()
        return

    curSysname = cur_syskey

    while ix < inp_max:
        # declare logEntries here so we always have a fresh one:
        logEntries = {}  # dictionary with log parameter as key, value as value

        # read in a full log entry:
        ix, inp_entry = getEntry(inp_file, ix, inp_max)

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
                if thisVal[0] != curSysname:
                    allSystems[curSysname] = datedEntries
                    datedEntries = {} # refresh
                    curSysname = thisVal[0]
            elif 'Datetime' in thisKey:
                logEntries[thisKey] = thisVal
            else:
                logEntries[thisKey] = thisVal

        # create datedEntries using the datestamp for its keys:
        datedEntries[dateKey] = logEntries

    # create allSystems with the system name for its keys:
    allSystems[curSysname] = datedEntries

# EOF:
