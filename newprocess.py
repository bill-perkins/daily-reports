# newprocess.py
# imported by pd.py
#
# Take a given log file and return the system name,
# along with all the dated entries in a dictionary
#

import sys
import lclvars
from utils import *
from parseentry import *
from systems import System
from datetime import datetime

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """ Bring the contents of the given input file into a list,
        and return the list.
        filename: name of the file we're processing (daily.log)
        returns:  deque of lines from given filename;
        sys.exit(1) if file not found or permissions error.
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

    logcontent.reverse()
    return logcontent

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

            if 'load' not in syskeys:
                sysobj.add_component('load')

            if parts[3] == 'days,':
                sysobj.add_usage('uptime', [dtobj, [parts[2], parts[3], parts[4]]])
            else:
                sysobj.add_usage('uptime', [dtobj, [parts[2], parts[3]]])

            sysobj.add_usage('load', [dtobj, [parts[-3], parts[-2], parts[-1]]])

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
                sysobj.add_component('Mem', parts[1])

            sysobj.add_usage('Mem', [dtobj, parts[2]])
            # finished here:
            continue

        # --- process Swap: entry:
        if line.startswith('Swap'):
            parts = line.split()
            if 'Swap' not in syskeys:
                sysobj.add_component('Swap', parts[1])

            sysobj.add_usage('Swap', [dtobj, parts[2]])
            # finished here:
            continue

        # --- process Filesystems:
        if line.startswith('Filesystem'):
            line = lines.pop()
            while len(line) > 1 and not line.startswith('----'):
                parts = line.split()
                if parts[5] not in syskeys:
                    sysobj.add_disk(parts[5], parts[1])

                sysobj.add_usage(parts[5], [dtobj, parts[2]])
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
            sysobj.add_usage('Services', [dtobj, parts[2]])

            # finished here:
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
