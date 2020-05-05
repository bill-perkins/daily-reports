#!/usr/bin/python
#
# pd.py- process daily.log
# simple script to take daily.log and convert to a dictionary,
# do some analysis of the data
#

# some standard python stuff
import sys
import os
import time
from datetime import datetime
from datetime import date
from datetime import timedelta

## for debugging:
#import pprint
#pp = pprint.PrettyPrinter(indent=2, width=160)

allSystems = {}  # Global dictionary as sysname: datedEntries
curSysname = ''  # Global current system name from logfile

# if a line starts with a day of the week, we want to add the
# hostname to the line.
starters = [ 'Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ', 'Sun ' ]

oneday = timedelta(days = 1)

iam = sys.argv[0]

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

    # open up the new file, bring it in as a list:
    try:
        with open(filename, "r") as inpfile:
            logcontent = inpfile.readlines()

    except IOError as err:
        print("getContent(): Couldn't open file " + filename + ": " + str(err))
        sys.exit(0)

    return logcontent

# ----------------------------------------------------------------------------
# getEntry(inpdata, index, maxindex)
# ----------------------------------------------------------------------------
def getEntry(inpdata, index, maxindex):
    """Bring in the lines from current index,
       until we see "----" in the line.
       input parameters:
           inpdata: list of lines from getContent()
           index:   line # we start processing at
           maxindex: last line index of inpdata
       returns:
           newindex: next index to process
           list of lines in this entry
    """

    newindex = index
    outlist = []
    while newindex < maxindex:
        outlist.append(inpdata[newindex])
        newindex += 1

        # Look ahead to the next line:
        # If it starts with '----', increment newindex to
        # move past the next line, and break out.
        if newindex < maxindex and inpdata[newindex][0:4] == '----':
            newindex += 1
            break

    # return the new index and the output list
    return newindex, outlist

# ----------------------------------------------------------------------------
# parseEntry(log_entry)
# ----------------------------------------------------------------------------
def parseEntry(log_entry):
    """Return a dictionary from a given log entry.
    """
    entry = []          # a list of key:value pairs
    global starters     # the list of day names, Mon-Fri
    global curSysname   # the name of the system we're currently working on

    # parse each line:
    while len(log_entry) > 0:
        inpline = log_entry.pop(0)[:-1]
        if len(inpline) == 0:
            continue # skip blank lines

        # see if we have to add the hostname to this line:
        if inpline[0:4] in starters:
            inpline = curSysname + ': ' + inpline

        # get system name, date, uptime, load average:
        if "corp.local" in inpline:
            parts = inpline.split(': ')

#            datestamp = datetime.datetime.strptime(parts[1], "%a %b %d %H:%M:%S %Z %Y")
            datestamp = datetime.strptime(parts[1], "%a %b %d %H:%M:%S %Z %Y")
            entry.append(['Datestamp:', str(datestamp.date())])
            entry.append(['Systime', str(datestamp.time())])
            entry.append(['Datetime', datestamp])
            entry.append(['Sysname', parts[0]]) # system name

            # snag the next line, it's got uptime, user count, load average
            uptime = log_entry.pop(0)[:-1]
            parts = uptime.split(',') # split on comma
            """
              parts[0] = 00:00:00 up 00 days,
              parts[1] = 00:00,
              parts[2] = 0 users,
              parts[3] = load average: 0.00
              parts[4] = 0.00
              parts[5] = 0.00
                or
              parts[0] = 00:00:00 up 00:00,
              parts[1] = 0 users,
              parts[2] = load average: 0.00
              parts[3] = 0.00
              parts[4] = 0.00
            """

            # get how long we've been up, days or hours:
            utparts = parts[0].split()
            """
              utparts[0] = time
              utparts[1] = 'up'
              utparts[2] = 00 (or 00:00:00)
              utparts[3] = 'days' (if utparts[2] is not a time)
            """

            ut = utparts[2]
            if len(utparts) == 4: # we have a 'days' in there
                ut += ' days,' + parts[1] # add days, then hh:mm from parts[1]

            entry.append(['Uptime:', ut])

            # get the load averages:
            # snag the last 3 fields from parts, fix up the 1st field

            load_list = ['Load:']
            load_list.extend([parts[-3].split()[2], parts[-2], parts[-1]])

            entry.append(['LoadHdr:', '1m','5m','15m'])
            entry.append(load_list)

            continue

        # get memory/cache and swap elements:
        if "buff/cache" in inpline: # we have the header; use it
            memhdr = ['Memhdr:']
            memhdr.extend(inpline.split())

            # now get the numbers:
            inpline = log_entry.pop(0)[:-1]
            memparts = inpline.split()

            # add the header and the numbers to entry:
            entry.append(memhdr)
            entry.append(memparts)

            # get the swap numbers:
            inpline = log_entry.pop(0)[:-1]
            swapparts = inpline.split()
            # just add the header directly:
            entry.append(['Swaphdr:', 'total', 'used', 'free'])
            entry.append(swapparts)

            continue

        # get disk usages:
        if "Use%" in inpline:
            entry.append(['Diskhdr:', 'Size', 'Used', 'Avail', 'Use%'])
            while len(inpline) > 1 and log_entry:
                inpline = log_entry.pop(0)[:-1]
                if len(inpline) > 0 and "----" not in inpline:
                    tmp = inpline.split()
                    entry.append([tmp[5], tmp[1], tmp[2], tmp[3], tmp[4]])

            continue

        # check ping test:
        if "ping test" in inpline:
            pingparts = inpline.split()
            entry.append(['ping test', pingparts[2]])

            continue

        # check services:
        if "services" in inpline:
            if inpline.split()[2] == 'OK':
                entry.append(['services', 'OK'])
            else:
                entry.append(['services', 'some services are DOWN:'])
                inpline = log_entry.pop(0)[:-1]
                downlist = []   # list of downed services
                while len(inpline) > 1:
                    parts = inpline.split()
                    downlist.append(parts[0])
                    inpline = log_entry.pop(0)[:-1]

                entry.append(['DOWN', downlist])
            continue

    return entry

# ----------------------------------------------------------------------------
# process()
# ----------------------------------------------------------------------------
def process(logfile):
    """Takes a given log file and adds the data to the global allSystems
    dictionary.
    """

    print 'processing:', logfile

    inp_file = getContent(logfile)      # get entire file into inp_file
    inp_max = len(inp_file)             # lines in file
    inp_index = 0                       # current index into inp_file
    cur_syskey = ''                     # current system name

    inp_entry = []                      # create local entry list
    out_entry = []                      # create local entry list

    datedEntries = {}                   # dictionary as datestamp: logEntries
    global allSystems                   # dictionary as sysname: datedEntries
    global curSysname
    curSystime = ''                     # system time of this entry

    for line in inp_file:
        if 'corp.local' in line:
            cur_syskey = line.split(':')[0]
            break;

    if cur_syskey == '':
        print "couldn't find system hostnme in", logfile
        print "skipping."
        print
        return
    curSysname = cur_syskey

    while inp_index < inp_max:
        # declare logEntries here so we always have a fresh one
        logEntries = {}  # dictionary with log parameter as key, value as value

        # read in a full log entry:
        inp_index, inp_entry = getEntry(inp_file, inp_index, inp_max)

        # parse the entry into a list of key:value pairs
        out_entry = parseEntry(inp_entry)

        # put the key:value pairs into the logEntries;
        # handle Datestring, Datestamp, and Sysname special:
        dateKey = ''    # fresh dateKey
        for x in out_entry:
            thisKey = x[0]
            thisVal = x[1:]

            if 'Datestamp:' in thisKey:
                dateKey = thisVal[0]
            elif 'Systime:' in thisKey:
                curSystime = thisKey
            elif 'Sysname' in thisKey:
                if thisVal[0] != curSysname:
                    allSystems[curSysname] = datedEntries
                    datedEntries = {}
                    curSysname = thisVal[0]
            elif 'Datetime' in thisKey:
                logEntries[thisKey] = thisVal
            else:
                logEntries[thisKey] = thisVal

        # create datedEntries using the datestamp for its keys:
        datedEntries[dateKey] = logEntries

    # create allSystems with the system name for its keys:
    allSystems[curSysname] = datedEntries

# ----------------------------------------------------------------------------
# analyze():
# ----------------------------------------------------------------------------
def analyze(systems):
    """Look for changing immutable values.
       Immutable values are set by the first log entry processed.
    """

    global oneday

    # invariants dictionary
    inv_d = {'/':        '', \
            '/opt/sas':  '', \
            '/sasdata':  '', \
            '/sastmp':   '', \
            'Mem:':      '', \
            'Swap:':     '', \
            'ping test': '', \
            'services':  '', \
            'Uptime:':   '' }

    print # to separate 'processing' lines from 'Analyzing' lines

    # --- now we want to analyze some of the data:
    for sysname, datedEntries in systems.items():
        nexttime = date(2020,1,3)
        print 'Analyzing system', sysname + ':'
        print

        # grab logs in date order:
        for datestamp in sorted(datedEntries):
            if datestamp == '':
                continue    # somehow, we get a blank datestamp. Skip it.

            # cur_entry is the dictionary for this datestamp
            cur_entry = datedEntries[datestamp]

            # get a date object for this datestamp:
            thisdate = date(int(datestamp[0:4]), \
                    int(datestamp[5:7]), \
                    int(datestamp[8:10]))

            # complain if we see something unexpected:
            if thisdate != nexttime:
                if str(nexttime) != '2020-01-03':
                    print thisdate, "expected datestamp:", nexttime
                else:
                    nexttime = thisdate
                    print thisdate, 'Logging starts'

            # create a date object for the next day:
            nexttime = thisdate + oneday

            """
                Search for changes to invariant data.
                When something comes up different, complain about it,
                then change the invariants list to the new value.
            """
            for key, value in inv_d.items():
                try:
                    val = cur_entry[key]
                except KeyError as err:
                    continue # key not there? Who cares?

                if key == 'Uptime:':
                    # Did we reboot?
                    if 'days' not in val[0]:
                        hm = val[0].split(':')
#                        dTime = datetime.timedelta(hours = int(hm[0]), minutes = int(hm[1]))
                        dTime = timedelta(hours = int(hm[0]), minutes = int(hm[1]))
                        cTime = cur_entry['Datetime'][0]
                        rebooted = cTime - dTime
                        print rebooted.date(), "Reboot @", rebooted.time()
                    continue

                if key == 'services' and inv_d['services'] == '':
                    inv_d['services'] = 'OK'
                    print thisdate, 'first appearance of services check'

                if key == 'ping test' and inv_d['ping test'] == '':
                    inv_d['ping test'] = 'OK'
                    print thisdate, 'first appearance of ping test'

                if len(value) > 0 and value != val[0]:
                    if key == 'services':
                        print thisdate, 'Some services were down:'
                        downlist = cur_entry['DOWN']
                        dLines = downlist[0]
                        for dLine in dLines:
                            print '          ', dLine
                        print
                    else:
                        print thisdate, key + ": expected: '" + value + \
                                "', found: '" + val[0] + "'"

                if key != 'services' \
                        and key != 'ping test' \
                        and key != 'Uptime:':
                    inv_d[key] = val[0]

        # final print to separate system reports:
        print

#------------------------------------------------------------------------------
# pretty-print the resulting dictionary:
#print "allSystems:"
#print
#pp.pprint(allSystems)
#print

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    if len(sys.argv) == 1:
        arglist = ['daily.log']
    else:
        arglist = sys.argv[1:]

    for inpfile in arglist:
        process(inpfile) # process() updates global allSystems{}

    analyze(allSystems)

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------

# EOF:
