# analyze.py
#
# this version replaces the original analyze.py and disk_analyze.py
#

# --- functions defined here:
# printminmaxavg(entries)
# chk4variant(size, variance, entries)
# analyze_load(variance, entries):
# analyze(sysname, sysdata, switches):

from datetime   import datetime
from datetime   import date
from datetime   import timedelta
from statistics import mean
from utils      import humanize

event_list = []     # final output list

ONEDAY = timedelta(days = 1) # timedelta of one day
DISKVARIANCE = 20.0         # disk variance we are looking for
SWAPVARIANCE = 10.0         # mem/swap variance we are looking for

# ----------------------------------------------------------------------------
# showusage(size, entries, name)
# ----------------------------------------------------------------------------
def showusage(size, entries, name):
    '''
    '''
    lclSize = size
    usepct  = 0

    for e in entries:
        thisdate = e[0].date()
        thistime = e[0].time()
        thisUsed = e[1]

# ----------------------------------------------------------------------------
# printminmaxavg(entries)
# ----------------------------------------------------------------------------
def printminmaxavg(entries):
    """ Print start, current, minimum, maximum, and average usage
    """
    values   = [int(e[1]) for e in entries]
    min_used = min(values)
    max_used = max(values)
    max_used_entry = entries[values.index(max_used)]
    min_used_entry = entries[values.index(min_used)]
    avg_used = mean(values)

    print('     started:', humanize(entries[0][1]),  'on', entries[0][0].date())
    print('   currently:', humanize(entries[-1][1]), 'on', entries[-1][0].date())
    print('    min used:', humanize(min_used),       'on', min_used_entry[0].date())
    print('    max used:', humanize(max_used),       'on', max_used_entry[0].date())
    print('    avg used:', humanize(avg_used))

# ----------------------------------------------------------------------------
# pctize()
# ----------------------------------------------------------------------------
def pctize(amt, outof):
#    percent = (amt / outof) * 100
#    percent = (float(amt) / float(outof)) * 100.0
    return (float(amt) / float(outof)) * 100.0

# ----------------------------------------------------------------------------
# chk4variant(size, variance, entries, name)
# ----------------------------------------------------------------------------
def chk4variant(size, variance, entries, name=''):
    """ Print any usage entry that goes outside of
        the given day-to-day variance.
    """
    lastUsed = 0
    last_e1 = '0'
    lastdate = date(2019, 1, 2)

    lclSize = size

    for e in entries:
        thisdate = e[0].date()
        thistime = e[0].time()
        if thisdate == lastdate:
            continue

        lastdate = thisdate
        # do something with the data we have
        #print('   ', thisdate, e[1], 'used out of', lclSize)
        thisUsed = e[1]
        if thisUsed != lastUsed:
            delta = thisUsed - lastUsed
            pct = (delta / lclSize) * 100

            h_e1 = humanize(e[1])
            h_l1 = humanize(last_e1)
            h_sz = humanize(size)
            p_e1 = f'{pctize(e[1], lclSize):.1f}'
            p_l1 = f'{pctize(last_e1, lclSize):.1f}'

            if pct > variance: # current hard-coded variance
                event_list.append(f'{str(thisdate)} {str.ljust(name, 12)}: {h_e1} ({p_e1}%) used out of {h_sz}, up from {h_l1} ({p_l1}%)')

            elif pct < -variance:
                event_list.append(f'{str(thisdate)} {str.ljust(name, 12)}: {h_e1} ({p_e1}%) used out of {h_sz}, dn from {h_l1} ({p_l1}%)')

            lastUsed = thisUsed
            last_e1  = e[1]

# ----------------------------------------------------------------------------
# analyze_load(variance, entries):
# ----------------------------------------------------------------------------
def analyze_load(variance, entries):
    """ Print out any major changes in usage entries
    """
    lastUsed = 0
    lastdate = date(2019, 1, 2)

    for e in entries:
        thisdate = e[0].date()
        thistime = e[0].time()
        if thisdate == lastdate:
            continue

        lastdate = thisdate

        # do something with the data we have:
        thisUsed = float(e[1][0])
        if thisUsed > variance:
            event_list.append(f'{str(thisdate)} Load        : {str(thisUsed)}, was {lastUsed}')

        lastUsed = thisUsed

# ----------------------------------------------------------------------------
# analyze(sysname, sysdata, switches):
# ----------------------------------------------------------------------------
def analyze(sysname, sysdata, switches):
    """ Look for entries to print
        sysname  is the name of the system we're investigating
        sysdata  is a dictionary, uses sysname as the key
        switches is a tuple of Booleans:
            switches[0] = show_events
            switches[1] = show_disk
            switches[2] = show_mem
            switches[3] = show_ping
    """

    global event_list   # final output list

    event_list = []     # start fresh
    variance = 19.9     # default variance

    nextdate = date(2019, 1, 2)
    lastdate = date(2019, 1, 2)
    thisdate = date(2019, 1, 3)
    show_events, show_disk, show_mem, show_ping = switches

    if sysname not in sysdata.keys():
        print('analyze(): system', sysname, 'not in sysdata dictionary.')
        return

    datedEntries = sysdata[sysname]
    if len(datedEntries) == 0:
        print('analyze(): no entries for', sysname)
        return

    print('# ----------------------------------------------------------------------------')
    print('Analyzing system', sysname + ':')
    print()

    # we have three keys: name, uptime, load:
    for sysptr in datedEntries:
        ''' datedEntries is a list of system objects
            sysptr is the dictionary for the given system name
        '''

        # --- uptime entries:
        entries = sysptr.get_entries('uptime')
        # entries is the list of of uptime entries
        for e in entries:
            # each 'e' is a list: [datetime, [list_of_words]]
            thisdate = e[0].date()
            thistime = e[0].time()
            if thisdate == lastdate:
                continue    # skip duplicate date entries

            lastdate = thisdate

            if thisdate != nextdate:
                if nextdate != date(2019, 1, 2):
                    event_list.append(f'{str(thisdate)} unexpected datestamp, expected: {str(nextdate)}')

            nextdate = thisdate + ONEDAY

            uptime = e[1]
            if 'days,' not in uptime and 'day,' not in uptime:
                # means that we rebooted less than a day ago,
                # so see if we can figure out when we did reboot:
                reboottime = uptime[0].rstrip(',')
                if 'min,' not in uptime:
                    lclhours, lclminutes = reboottime.split(':')
                else:
                    lclhours = '0';
                    lclminutes = uptime[0]

                ago = timedelta(hours = int(lclhours), minutes = int(lclminutes))
                rebootdate = e[0] - ago
                event_list.append (str(rebootdate.date()) + ' Rebooted    : ' + str(rebootdate.time()))

        # --- load entries:
        entries = sysptr.get_entries('load')
        sp      = sysptr.get_component('load')
        # get_component() returns a dictionary (key 'entries') with a list of entries
        analyze_load(5.0, sp['entries'])

        # --- Memory entries:
        entries = sysptr.get_entries('Mem')
        sp      = sysptr.get_component('Mem')
        # get_component returns a dictionary (key 'entries', 'size'):
        # entries is a list, each value is a list [datetime, size_in_bytes]
        chk4variant(sp['size'], SWAPVARIANCE, entries, 'Mem')
        if show_mem:
            print('Memory (' + humanize(sp['size']) + '):')
            printminmaxavg(entries)
            print()

        # --- Swap entries:
        entries = sysptr.get_entries('Swap')
        sp      = sysptr.get_component('Swap')
        # get_component returns a dictionary (key 'entries', 'size'):
        # entries is a list, each value is a list [datetime, size_in_bytes]
        chk4variant(sp['size'], SWAPVARIANCE, entries, 'Swap')
        if show_mem:
            print('Swap (' + humanize(sp['size']) + '):')
            printminmaxavg(entries)
            print()

        # --- Ping entries:
        if show_ping:
            entries = sysptr.get_entries('Ping')
            # get_entries() returned a list of [datetime, 'OK'] or error messages
            print('Ping entries:')
            ping_ok = True      # preset
            for e in entries:
                thisdate = e[0].date()
                thistime = e[0].time()
                if thisdate == lastdate:
                    continue

                lastdate = thisdate

                # do something with the data we have
                if e[1] != 'OK':    # flag it
                    print(f'    {str(thisdate)} - {e[1]}')
                    event_list.append(str(thisdate) + ' ' + e[1])
                    ping_ok = False

            if ping_ok == True:
                print('    Ping tests all OK')

            print()

        # --- Services entries:
        entries = sysptr.get_entries('Services')
        # get_entries() returned a list of [datetime, 'OK'] or error messages
        for e in entries:
            thisdate = e[0].date()
            thistime = e[0].time()
            if thisdate == lastdate:
                continue

            lastdate = thisdate

            # do something with the data we have
            if e[1][0] != 'OK':
                tmpstr = str(thisdate) + ' ' + e[1][0] + '\n'
                if type(e[1]) == type([]):
                    y = e[1]
                    for x in y[1:]:
                        tmpstr += '             ' + x + '\n'
                event_list.append(tmpstr)

        # --- Disk entries:
        disklist = sysptr.get_dskkeys()
        for disk in disklist:
            lcldisksize = sysptr.get_dsksize(disk)
            ''' entries is a list of a datetime and a size '''
            entries = sysptr.get_entries(disk)
            if entries != None:

                # - scan for changes >10% of current usage
                chk4variant(size=lcldisksize, variance=DISKVARIANCE, entries=entries, name=disk)

                # - show min, max, average daily usage
                if show_disk:
                    print("'{}' ({}):".format(disk, humanize(lcldisksize)))
                    printminmaxavg(entries)
                    print()

        # --- Other entries:
        entries = sysptr.get_entries('<entry>')
        if entries != None:
            print('<entry> entries:')
            for e in entries:
                thisdate = e[0].date()
                thistime = e[0].time()
                if thisdate == lastdate:
                    continue

                lastdate = thisdate
                # do something with the data we have

            print()

    if show_events:
        event_list.sort()
        print('Events:')
        print()
        print(f'{event_list[0][:10]} Logging starts')
        for x in event_list:
            print(x)
        print()

    pass

# EOF:
