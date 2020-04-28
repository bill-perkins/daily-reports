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
from datetime import date
from datetime import timedelta

import pprint # for development

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
           index:   line # we start processing
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
        # If it starts with '----',
        # increment newindex to move past the next line, and break out,
        # we've reached the end of the entry.
        if newindex < maxindex and inpdata[newindex].startswith('----'):
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
    entry = []

    # parse each line:
    while len(log_entry) > 0:
        inpline = log_entry.pop(0)[:-1]
        if len(inpline) == 0:
            continue # skip blank lines

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
            uptime = log_entry.pop(0)[:-1]

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
            svcparts = inpline.split()
            entry.append(['services', svcparts[2]])

            continue

    return entry

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
inp_file = getContent('daily.log') # get entire file into inp_file
inp_max = len(inp_file)            # lines in file
inp_index = 0                      # current index into inp_file

inp_entry = []  # create local entry list
out_entry = []  # create local entry list

allSystems = {}   # dictionary with sysname as key, datedEntries as value
datedEntries = {} # dictionary with datestamp as key, entries as value

pp = pprint.PrettyPrinter(indent=2, width=160)

# grab a chunk of the file, up to "------":
inp_index, inp_entry = getEntry(inp_file, inp_index, inp_max)

while len(inp_entry) > 1:
    # declare entries here so we always have a fresh one
    logEntries = {}  # dictionary with various entries as keys: uptime, mem, etc.
    out_entry = parseEntry(inp_entry)
    dateKey = ''
    for x in out_entry:
        thisKey = x[0]
        thisVal = x[1:]

        if 'Datestring:' in thisKey:
            logEntries[thisKey] = thisVal
            continue

        if 'Datestamp:' in thisKey:
            dateKey = thisVal[0]
            continue

        if 'Sysname:' in thisKey:
            sysKey = thisVal[0]
            continue

        if 'Uptime:' in thisKey:
            logEntries[thisKey] = thisVal
            continue

        if 'Load:' in thisKey:
            logEntries[thisKey] = thisVal
            continue

        if 'Mem:' in thisKey:
            logEntries[thisKey] = thisVal
            continue

        if 'Swap:' in thisKey:
            logEntries[thisKey] = thisVal
            continue

        if '/' in thisKey:
            logEntries[thisKey] = thisVal
            continue

        if 'ping' in thisKey:
            logEntries[thisKey] = thisVal

        if 'services' in thisKey:
            logEntries[thisKey] = thisVal

#        # default:
#        logEntries[thisKey] = thisVal
#        continue

    # create datedEntries using the datestamp for its keys:
    datedEntries[dateKey] = logEntries

    # get the next inp_entry:
    inp_index, inp_entry = getEntry(inp_file, inp_index, inp_max)

# create allSystems with the system name for its keys:
allSystems[sysKey] = datedEntries

#------------------------------------------------------------------------------
# pretty-print the resulting dictionary:
print "allSystems:"
print
pp.pprint(allSystems)
print

delta1 = timedelta(days = 1)

inv_d = {'/': 0, '/opt/sas': 0, '/sasdata': 0, 'sastmp': 0, 'Mem': 0, 'Swap': 0 }

invariants = [] # list of invariant values
invkeylist = ['/', '/opt/sas', '/sasdata', '/sastmp', 'Mem:', 'Swap:', 'ping test', 'services', 'Uptime:']

# --- initialize the invariants list:
for x in invkeylist:
    invariants.append('') # initialize

print 'Analyzing:'

# --- now we want to analyze some of the data:
for sysname, datedEntries in allSystems.items():
    nexttime = date(2020,1,3)

    print 'sysname:', sysname

    # grab logs in date order:
    for datestamp in sorted(datedEntries):
        if datestamp == '':
            continue    # somehow, we get a blank datestamp. Skip it.

        cur_entry = datedEntries[datestamp] # d2 is the dictionary for this datestamp
        cur_date = cur_entry['Datestring:'][0] + ':'

        # get a date object for this datestamp:
        thistime = date(int(datestamp[0:4]), \
            int(datestamp[4:6]), \
            int(datestamp[6:8]))

        # complain if we see something unexpected:
        if thistime != nexttime:
            print cur_date, "expected datestamp:", nexttime, "- found:", thistime

        # create a date object for the next day:
        nexttime = thistime + delta1

        """
        Notes:
            Invariant entries:
                key '/'         val[0]
                key '/opt/sas'  val[0]
                key '/sasdata'  val[0]
                key '/sastmp'   val[0]
                key 'Mem:'      val[0]
                key 'Swap:'     val[0]
                key 'ping test' val[0] should always be 'OK'
                key 'services'  val[0] should always be 'OK'
                key 'Uptme:'    val[0] should always have 'days'

                Set invariant entries from the first entry

            When looping through the dictionary, get the first date, then add a day
            each iteration and create the next key. Make sure the key exists, if not,
            flag it, add a day and iterate again until the end.
        """

        """
            search for changes to invariant data
            when something comes up different, complain about it,
            then change the invariants list to the new value.
        """
#        val = cur_entry['/'][0]
#        if invariants[0] != val:
#            if len(invariants[0]) > 0:
#                print cur_date, "'/': expected:", invariants[0], "- found:", val
#            invariants[0] = val

        # change to:
        # for key in invkeylist:
        key = invkeylist[0]

        val = cur_entry[key][0]

        val = cur_entry['/opt/sas'][0]
        if invariants[1] != val:
            if len(invariants[1]) > 0:
                print cur_date, "'/opt/sas': expected:", invariants[1], "- found:", val
            invariants[1] = val

        val = cur_entry['/sasdata'][0]
        if invariants[2] != val:
            if len(invariants[2]) > 0:
                print cur_date, "'/sasdata': expected:", invariants[2], "- found:", val
            invariants[2] = val

        val = cur_entry['/sastmp'][0]
        if invariants[3] != val:
            if len(invariants[3]) > 0:
                print cur_date, "'/sastmp': expected:", invariants[3], "- found:", val
            invariants[3] = val

        val = cur_entry['Mem:'][0]
        if invariants[4] != val:
            if len(invariants[4]) > 0:
                print cur_date, "'Mem': expected:", invariants[4], "- found:", val
            invariants[4] = val

        val = cur_entry['Swap:'][0]
        if invariants[5] != val:
            if len(invariants[5]) > 0:
                print cur_date, "'Swap': expected:", invariants[5], "- found:", val
            invariants[5] = val

        if cur_entry.get('ping test', 'no key') != 'no key':
            val = cur_entry['ping test'][0]
            if invariants[6] != val:
                if len(invariants[6]) > 0:
                    print cur_date, "Ping test: expected:", invariants[6], "- found:", val
                else:
                    print cur_date, "first day of ping tests"

                invariants[6] = val

        if cur_entry.get('services', 'no key') != 'no key':
            val = cur_entry['services'][0]
            if val != 'OK':
                print cur_date, "Some services were down"

            if invariants[7] != 'OK':
                if len(invariants[7]) > 0:
                    print cur_date, "Some services were down"
                else:
                    print cur_date, "first day of services checks"
                    invariants[7] = 'OK'

        val = cur_entry['Uptime:'][0]
        if 'days' not in val:
            print cur_date, "Rebootied"

##        extract values from specific key-
#        values = entries['Mem:']
#        print k1,values[0]

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------

# EOF:
