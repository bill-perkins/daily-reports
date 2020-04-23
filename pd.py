#!/usr/bin/python
# pd.py- parsedaily
# simple script to take daily.log and convert to a dictionary
#

# some standard python stuff
import sys
import os
import time
from datetime import date
from datetime import timedelta

import pprint # for development

iam = sys.argv[0]

# ----------------------------------------------------------------------------
# getContent(inpname)
# ----------------------------------------------------------------------------
def getContent(inpname):
    """bring the contents of the given input file into a list,
    and return the list.
    """

    logcontent = []

    # open up the new file, bring it in as a list:
    try:
        with open(inpname, "r") as inpfile:
            logcontent = inpfile.readlines()

    except IOError as err:
        print("getContent(): Couldn't open file " + inpname + ": " + str(err))

    return logcontent

# ----------------------------------------------------------------------------
# getEntry()
# ----------------------------------------------------------------------------
def getEntry(inpfile, index, maxindex):
    """bring in a list of lines from current index,
    until we see "----" in the line.
    """
    entry = []
    while index < maxindex:
        entry.append(inpfile[index])
        index += 1
        if index < maxindex:
            if inpfile[index].startswith('----'):
                index += 1
                break

    return index, entry

# ----------------------------------------------------------------------------
# parseEntry(contents)
# ----------------------------------------------------------------------------
def parseEntry(contents):
    """return a dictionary given a log entry."""
    entry = []
    # parse each line:
    while len(contents) > 0:
        inpline = contents.pop(0)[:-1]
        if len(inpline) == 0:
            continue; # skip blank lines

        # get system name, date, uptime, load average:
        if "corp.local" in inpline:
            parts = inpline.split(': ')
            entry.append(['Datestring:', parts[1]]) # entry date
            datestamp = time.strptime(parts[1], "%a %b %d %H:%M:%S %Z %Y")
            entry.append(['Datestamp:', str(datestamp.tm_year) + \
                '%02d' % (datestamp.tm_mon) + \
                '%02d' % (datestamp.tm_mday)])
            entry.append(['Sysname:', parts[0]]) # system name

            # snag the next line, it's got uptime, user count, load average
            uptime = contents.pop(0)[:-1]

            parts = uptime.split(',') # split on comma
            # parts[0] = 00:00:00 up 00 days,
            # parts[1] = 00:00,
            # parts[2] = 0 users,
            # parts[3] = load average: 0.00
            # parts[4] = 0.00
            # parts[5] = 0.00
            #   or
            # parts[0] = 00:00:00 up 00:00,
            # parts[1] = 0 users,
            # parts[2] = load average: 0.00
            # parts[3] = 0.00
            # parts[4] = 0.00

            # get how long we've been up, days or hours:
            utparts = parts[0].split()
            # utparts[0] = time
            # utparts[1] = 'up'
            # utparts[2] = 00 (or 00:00:00)
            # utparts[3] = 'days' (if utparts[2] is not a time)

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
            inpline = contents.pop(0)[:-1]
            memparts = inpline.split()

            # add the header and the numbers to entry:
            entry.append(memhdr)
            entry.append(memparts)

            # get the swap numbers:
            inpline = contents.pop(0)[:-1]
            swapparts = inpline.split()
            # just add the header directly:
            entry.append(['Swaphdr:', 'total', 'used', 'free'])
            entry.append(swapparts)

            continue

        # get disk usages:
        if "Use%" in inpline:
            entry.append(['Diskhdr:', 'Size', 'Used', 'Avail', 'Use%'])
            while len(inpline) > 1 and contents:
                inpline = contents.pop(0)[:-1]
                if len(inpline) > 0 and "----" not in inpline:
                    tmp = inpline.split()
                    entry.append([tmp[5], tmp[1], tmp[2], tmp[3], tmp[4]])

            continue

        if "ping test" in inpline:
            pingparts = inpline.split()
            entry.append(['ping test', pingparts[2]])

    return entry

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
logFile = getContent('daily.log')   # get entire file into logFile
#logFile = getContent('new-single')   # get entire file into logFile
logFileMax = len(logFile)           # lines in file
logFileIndex = 0                    # current index into logFile

inp_entry = []  # create local entry list
out_entry = []  # create local entry list

dict0 = {}  # dictionary with sysname as key, dict1 as value
dict1 = {}  # dictionary with datestamp as key, dict2 as value

pp = pprint.PrettyPrinter(indent=2, width=160)

# grab a chunk of the file, up to "------":
logFileIndex, inp_entry = getEntry(logFile, logFileIndex, logFileMax)
while len(inp_entry) > 1:
    # declare dict2 here so we always have a fresh one
    dict2 = {}  # dictionary with various entries as keys: uptime, mem, etc.
    out_entry = parseEntry(inp_entry)
    dateKey = ''
    for x in out_entry:
        theKey = x[0]
        theVal = x[1:]

        if 'Datestring:' in theKey:
            dict2[theKey] = theVal
            # dateString = theVal[0]
            continue;

        if 'Datestamp:' in theKey:
            dateKey = theVal[0]
            continue

        if 'Sysname:' in theKey:
            sysKey = theVal[0]
            continue

        if 'Uptime:' in theKey:
            dict2[theKey] = theVal
            continue;

        if 'Load:' in theKey:
            dict2[theKey] = theVal
            continue

        if 'Mem:' in theKey:
            dict2[theKey] = theVal
            continue

        if 'Swap:' in theKey:
            dict2[theKey] = theVal
            continue;

        if '/' in theKey:
            dict2[theKey] = theVal
            continue;

        # default:
        dict2[theKey] = theVal
        continue;

    # create dict1 using the datestamp for its keys:
    dict1[dateKey] = dict2

    # get the next inp_entry:
    logFileIndex, inp_entry = getEntry(logFile, logFileIndex, logFileMax)

# create dict0 with the system name for its keys:
dict0[sysKey] = dict1

#------------------------------------------------------------------------------
# pretty-print the resulting dictionary:
print "dict0:"
print
pp.pprint(dict0)
print

delta1 = timedelta(days=1)

invariants = []
invkeylist = ['/', '/opt/sas', '/sasdata', '/sastmp', 'Mem:', 'Swap:']

# --- initialize the invariants list:
for x in invkeylist:
    invariants.append('')

print 'Analyzing:'

# --- now we want to analyze some of the data:
for sysname,dict1 in dict0.items():
    nexttime = date(2020,1,3)

    print 'sysname:', sysname

    for datestamp in sorted(dict1):
        if datestamp == '':
            continue

        # grab logs in date order:
        d2 = dict1[datestamp]
        thisDate = d2['Datestring:'][0] + ':'

        # get a date object for this datestamp:
        thistime = date(int(datestamp[0:4]), \
            int(datestamp[4:6]), \
            int(datestamp[6:8]))

        # complain if we see something unexpected:
        if thistime != nexttime:
            print thisDate, "expected datestamp:", nexttime, "- found:", thistime

        # create a date object for the next day:
        nexttime = thistime + delta1

        """
        Invariant entries:
            key '/' val[0]
            key '/opt/sas' val[0]
            key '/sasdata' val[0]
            key '/sastmp'  val[0]
            key 'Mem:'     val[0]
            key 'Swap:'    val[0]

            Set invariant entries from the first entry

            When looping through the dictionary, get the first date, then add a day
            each iteration and create the next key. Make sure the key exists, if not,
            flag it, add a day and iterate again until the end.

            search for changes to invariant data
            when something comes up different, complain about it,
            then change the invariants list to the new value.
        """
        val = d2['/'][0]
        if invariants[0] != val:
            if len(invariants[0]) > 0:
                print thisDate, "'/': expected:", invariants[0], "- found:", val
            invariants[0] = val

        val = d2['/opt/sas'][0]
        if invariants[1] != val:
            if len(invariants[1]) > 0:
                print thisDate, "'/opt/sas': expected:", invariants[1], "- found:", val
            invariants[1] = val

        val = d2['/sasdata'][0]
        if invariants[2] != val:
            if len(invariants[2]) > 0:
                print thisDate, "'/sasdata': expected:", invariants[2], "- found:", val
            invariants[2] = val

        val = d2['/sastmp'][0]
        if invariants[3] != val:
            if len(invariants[3]) > 0:
                print thisDate, "'/sastmp': expected:", invariants[3], "- found:", val
            invariants[3] = val

        val = d2['Mem:'][0]
        if invariants[4] != val:
            if len(invariants[4]) > 0:
                print thisDate, "'Mem': expected:", invariants[4], "- found:", val
            invariants[4] = val

        val = d2['Swap:'][0]
        if invariants[5] != val:
            if len(invariants[5]) > 0:
                print thisDate, "'Swap': expected:", invariants[5], "- found:", val
            invariants[5] = val

##        extract values from specific key-
#        values = dict2['Mem:']
#        print k1,values[0]

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------

# EOF:
