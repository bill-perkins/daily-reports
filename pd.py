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

pp = pprint.PrettyPrinter(indent=2, width=160)

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
        # increment newindex to move past the next line, and break out.
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
            svcparts = inpline.split()
            entry.append(['services', svcparts[2]])

            continue

    return entry

# ----------------------------------------------------------------------------
# analyze():
# ----------------------------------------------------------------------------
def analyze(allSystems):
    delta1 = timedelta(days = 1)

    print 'Analyzing:'

    # invariants dictionary
    inv_d = {'/': '', \
            '/opt/sas':  '',   \
            '/sasdata':  '',   \
            '/sastmp':    '',  \
            'Mem:':      '',   \
            'Swap:':     '',   \
            'ping test': 'OK', \
            'services':  'OK', \
            'Uptime:':   '' }

    # --- now we want to analyze some of the data:
    for sysname, datedEntries in allSystems.items():
        nexttime = date(2020,1,3)

        print 'sysname:', sysname

        # grab logs in date order:
        for datestamp in sorted(datedEntries):
            if datestamp == '':
                continue    # somehow, we get a blank datestamp. Skip it.

            cur_entry = datedEntries[datestamp] # cur_entry is the dictionary for this datestamp
            cur_date = cur_entry['Datestring:'][0] + ':'

            # get a date object for this datestamp:
            thistime = date(int(datestamp[0:4]), int(datestamp[4:6]), int(datestamp[6:8]))

            # complain if we see something unexpected:
            if thistime != nexttime:
                print cur_date, "expected datestamp:", nexttime, "- found:", thistime

            # create a date object for the next day:
            nexttime = thistime + delta1

            """
                search for changes to invariant data
                when something comes up different, complain about it,
                then change the invariants list to the new value.
            """

            for key, value in inv_d.items():
                if cur_entry.get(key, 'no') != 'no':
                    logval = cur_entry[key][0]
                    if key == 'Uptime:':
                        if "days" not in logval:
                            print cur_date, "Rebootied:", logval, "hours ago"
                    elif len(value) > 0 and value != logval:
                        if key == 'services':
                            print cur_date, "Some services were down"
                        else:
                            print cur_date, key + ": expected: '" + value + "', found: '" + logval + "'"

                    if key != 'services' and key != 'ping test' and key != 'Uptime:':
                        inv_d[key] = logval

# ----------------------------------------------------------------------------
# process()
# ----------------------------------------------------------------------------
def process(logfile):
    inp_file = getContent(logfile) # get entire file into inp_file
    inp_max = len(inp_file)            # lines in file
    inp_index = 0                      # current index into inp_file

    inp_entry = []                     # create local entry list
    out_entry = []                     # create local entry list

    allSystems = {}                    # dictionary as sysname: datedEntries
    datedEntries = {}                  # dictionary as datestamp: logEntries

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

            if 'Datestring:' in thisKey:
                logEntries[thisKey] = thisVal
            elif 'Datestamp:' in thisKey:
                dateKey = thisVal[0]
            elif 'Sysname:' in thisKey:
                sysKey = thisVal[0]
            else:
                logEntries[thisKey] = thisVal

        # create datedEntries using the datestamp for its keys:
        datedEntries[dateKey] = logEntries

    # create allSystems with the system name for its keys:
    allSystems[sysKey] = datedEntries
    return allSystems

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
    allSystems = process('daily.log')
    analyze(allSystems)

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------

# EOF:
