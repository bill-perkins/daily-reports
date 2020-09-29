# newprocess.py
# imported by pd.py
#
# Take a given log file and return the system name,
# along with all the dated entries in a dictionary
#
# this one replaces the original process.py and parseentry.py

import sys
from utils import *
from systems import System
from datetime import datetime

# ----------------------------------------------------------------------------
# gather_data()
# ----------------------------------------------------------------------------
def gather_data(lines):
    """ Parse given data, extract useful information:
    """
    sysobjlist  = []    # list of System objects
    sysnamelist = []    # list of system names
    sysname     = ''    # current system name
    sDate       = ''    # current system date
    sTime       = ''    # current system time
    newsystem   = True  # used to create disk objects in new system entries
    sysobj      = None  # current system object
    dtobj       = None  # current date/time object
    syskeys     = []    # current set of system keys

    # main processing loop:
    while len(lines) > 1:
        line = lines.pop()
        if len(line) == 1:
            continue                    # skip blank lines

        # --- get initial system info:
        if 'corp.loca' in line and ' ping ' not in line:
            # get_initial_info(lines, line)

            sysname = line.split(':')[0]

            # sanity check: no hostname = we don't have sysname
            if sysname == '':
                print("can't find hostname in", logfile)
                print('...skipped...')
                print()
                return None, None

            # extract date, time:
            # datestr = ['day', 'month', 'date', 'time', 'tz', 'year']
            datelist = line.split(':',1)[1]
            dtobj = datetime.strptime(datelist, ' %a %b %d %H:%M:%S %Z %Y\n')

            if sysname not in sysnamelist:
                # set up a new system, sysobjlist:
                sysobjlist.append(System(sysname))
                sysnamelist.append(sysname)
                sysobj = sysobjlist[-1]
            else:
                sysobj = sysobjlist[sysnamelist.index(sysname)]

            syskeys = sysobj.get_keys()

            # get the next line: it's the time, uptime, user count, load average line:
            # we'll use sysobj.add_component()
            line = lines.pop()
            if 'up' not in line:
                print('"up" not found in line: \'' + line + "'")
                continue

            parts = line.split()
            if 'uptime' not in syskeys:
                sysobj.add_component('uptime')

            if parts[3] == 'days,':
                sysobj.add_usage('uptime', [dtobj, [parts[2], parts[3], parts[4]]])
            else:
                sysobj.add_usage('uptime', [dtobj, [parts[2], parts[3]]])

            if 'load' not in syskeys:
                sysobj.add_component('load')

            sysobj.add_usage('load', \
                    [dtobj, \
                    [parts[-3].rstrip(','), \
                    parts[-2].rstrip(','), \
                    parts[-1].rstrip(',')]])

            # get the next line: it's USER TTY FROM ...
            line = lines.pop()

            # keep popping lines until we hit a blank:
            while len(line) > 1:
                line = lines.pop()

            # finished here:
            continue

        # --- process Mem: entry:
        if line.startswith('Mem:'):
            parts = line.split()
            if 'Mem' not in syskeys:
                sysobj.add_component('Mem', dHumanize(parts[1]))

            sysobj.add_usage('Mem', [dtobj, dHumanize(parts[2])])
            # finished here:
            continue

        # --- process Swap: entry:
        if line.startswith('Swap'):
            parts = line.split()
            if 'Swap' not in syskeys:
                sysobj.add_component('Swap', dHumanize(parts[1]))

            sysobj.add_usage('Swap', [dtobj, dHumanize(parts[2])])
            # finished here:
            continue

        # --- process Filesystems:
        if line.startswith('Filesystem'):
            line = lines.pop()
            while len(line) > 1 and not line.startswith('----'):
                parts = line.split() # parts[1] is disk size, parts[5] is mount point
                if parts[5] not in syskeys:
                    sysobj.add_disk(parts[5], dHumanize(parts[1]))

                sysobj.add_usage(parts[5], [dtobj, dHumanize(parts[2])]) # parts[2] is usage
                line = lines.pop()

            # finished here:
            continue

        # --- snag the IP address:
        if 'MULTICAST' in line:
            line = lines.pop()
            parts = line.split()
            sysobj.set_ip_address(parts[1])

            # finished here:
            continue

        # --- ping test:
        if line.startswith('ping test'):
            if 'Ping' not in syskeys:
                sysobj.add_component('Ping')

            parts = line.split()
            sysobj.add_usage('Ping', [dtobj, parts[2]])

            # finished here:
            continue

        # --- services check:
        if line.startswith('services check'):
            if 'Services' not in syskeys:
                sysobj.add_component('Services')

            parts = line.split()
            if parts[2] == 'OK':
                sysobj.add_usage('Services', [dtobj, parts[2:]])
                continue

            outlist = ['Some services were DOWN:']
            newline = lines.pop()
            while len(newline) > 1:
                parts = newline.split()
                outlist.append(parts[0])
                newline = lines.pop()

            # finished here:
            sysobj.add_usage('Services', [dtobj, outlist])
            continue

        # NOTE: parse and process other lines here
        else:
            continue                    # skip lines we know nothing about

    return sysname, sysobjlist
    # end gather_data()

# ----------------------------------------------------------------------------
# process(logfile)
# ----------------------------------------------------------------------------
def process(logfile):
    """ Take a given log file and return the system name,
        along with all the dated entries in a dictionary
    """

    print('processing log file:', logfile)
    loglines = getContent(logfile)
    return gather_data(loglines)

# EOF:
