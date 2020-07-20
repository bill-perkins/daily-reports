# parseentry.py

from datetime import datetime

from utils import *

import lclvars

# ----------------------------------------------------------------------------
# get_initial()
# ----------------------------------------------------------------------------
def get_initial(inpline, log_entry, entry):

    parts = inpline.split(': ')

    datestamp = datetime.strptime(parts[1], '%a %b %d %H:%M:%S %Z %Y')

    entry.append(['Datestamp', str(datestamp.date())])
    entry.append(['Systime', str(datestamp.time())])
    entry.append(['Datetime', datestamp])
    entry.append(['Sysname', parts[0]]) # system name

    # snag the next line, it's got uptime, user count, load average
    uptime = log_entry.pop()

    parts = uptime.split(',') # split on comma

    #  parts[0] = 00:00:00 up 00 days,
    #  parts[1] = 00:00,
    #  parts[2] = 0 users,
    #  parts[3] = load average: 0.00
    #  parts[4] = 0.00
    #  parts[5] = 0.00
    #    or
    #  parts[0] = 00:00:00 up 00:00,
    #  parts[1] = 0 users,
    #  parts[2] = load average: 0.00
    #  parts[3] = 0.00
    #  parts[4] = 0.00

    # get how long we've been up, days or hours:
    utparts = parts[0].split()

    #  utparts[0] = time
    #  utparts[1] = 'up'
    #  utparts[2] = 00 (or 00:00:00)
    #  utparts[3] = 'days' (if utparts[2] is not a time)

    ut = utparts[2]
    if len(utparts) == 4: # we have a 'days' in there
        ut += ' days,' + parts[1] # add days, then hh:mm from parts[1]

    entry.append(['Uptime', ut])

    # get the load averages:
    # snag the last 3 fields from parts, fix up the 1st field
    load_list = ['Load']
    load_list.extend([parts[-3].split()[2], parts[-2], parts[-1]])

    entry.append(['LoadHdr', '1m','5m','15m'])
    entry.append(load_list)

# ----------------------------------------------------------------------------
# get_memory()
# ----------------------------------------------------------------------------
def get_memory(inpline, log_entry, entry):
    memhdr = ['Memhdr:']
    memhdr.extend(inpline.split())

    # now get the numbers:
    inpline = log_entry.pop()
    memparts = inpline.split()
    newmem = ['Mem']
    for n in memparts[1:]:
        newmem.append(ms2bytes(n))

    # add the header and the numbers to entry:
    entry.append(memhdr)
    entry.append(newmem)

    # get the swap numbers:
    inpline = log_entry.pop()
    swapparts = inpline.split()
    newswap = ['Swap']
    for n in swapparts[1:]:
        newswap.append(ms2bytes(n))

    # just add the header directly:
    entry.append(['Swaphdr:', 'total', 'used', 'free'])
    entry.append(newswap)

# ----------------------------------------------------------------------------
# parseEntry(log_entry)
# ----------------------------------------------------------------------------
def parseEntry(log_entry):
    """ Return a dictionary from a given log entry.
    """

    entry = []          # a list of key:value pairs
    log_entry.reverse()

    # parse each line:
    while len(log_entry) > 0:
        inpline = log_entry.pop().strip()
        if len(inpline) == 0:
            continue # skip blank lines

        # see if we have to add the hostname to this line:
        if inpline[0:4] in starters:
            inpline = lclvars.curSysname + ': ' + inpline

        # get system name, date, uptime, load average:
        if ' EST ' in inpline or ' EDT ' in inpline:
            get_initial(inpline, log_entry, entry)
            continue

        # get memory/cache and swap elements:
        if 'buff/cache' in inpline: # we have the header; use it
            get_memory(inpline, log_entry, entry)
            continue

        # get disk usages:
        if 'Use%' in inpline:
            entry.append(['Diskhdr', 'Size', 'Used', 'Avail', 'Use%'])
            while len(inpline) > 0 and log_entry:
                inpline = log_entry.pop().strip()
                if len(inpline) > 0 and '----' not in inpline:
                    parts = inpline.split()
                    entry.append([parts[5], \
                            to_bytes(parts[1]), \
                            to_bytes(parts[2]), \
                            to_bytes(parts[3]), \
                            to_bytes(parts[4])]) # disk name, size, used, free, use%
            continue

        # check ping test:
        if 'ping test' in inpline:
            pingparts = inpline.split()
            entry.append(['ping test', pingparts[2]])

            continue

        # check services:
        if 'services' in inpline:
            downlist = []   # list of downed services
            parts = inpline.split()
            if len(parts) > 2: # likely from one of the Viya servers
                if inpline.split()[2] == 'OK':
                    entry.append(['services', 'OK'])
                else:
                    entry.append(['services', 'some services were DOWN:'])
                    inpline = log_entry.pop()
                    while len(inpline) > 1:
                        if 'Consul' in inpline:
                            inpline = log_entry.pop()
                            continue

                        parts = inpline.split()
                        if 'Denodo' in parts[0]: # HACK
                            downlist.append(inpline.rstrip())
                        else:
                            downlist.append(parts[0])

                        if len(log_entry) > 0:
                            inpline = log_entry.pop()
                        else:
                            break

                    entry.append(['DOWN', downlist])

                continue
            else: # from the Denodo service
                entry.append(['services', 'denodo services:'])
                inpline = log_entry.pop()
                while len(inpline) > 1:
                    if 'is running' not in inpline and 'OK' not in inpline:
                        downlist.append(inpline.rstrip())
                    if len(log_entry) > 0:
                        inpline = log_entry.pop()
                    else:
                        inpline = ''
                entry.append(['DOWN', downlist])

    return entry

# EOF:
