# analyze.py
#
# this version replaces the original analyze.py and disk_analyze.py
#

from datetime import date
from datetime import timedelta
from statistics import mean

from utils import humanize, oneday
event_list = []     # final output list

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

    print('     started:', humanize(entries[0][1]), 'on', entries[0][0].date())
    print('   currently:', humanize(entries[-1][1]), 'on', entries[-1][0].date())
    print('    min used:', humanize(min_used), 'on', min_used_entry[0].date())
    print('    max used:', humanize(max_used), 'on', max_used_entry[0].date())
    print('    avg used:', humanize(avg_used))

# ----------------------------------------------------------------------------
# chk4variant(size, variance, entries)
# ----------------------------------------------------------------------------
def chk4variant(size, variance, entries, name=''):
    """ Print any usage entry that goes outside of
        the given day-to-day variance.
    """
    lastUsed = 0
    last_e1 = '0'
    lastdate = date(2019, 1, 2)

    lclSize = size

    if name != '':
        name = ' on ' + name

    for e in entries:
        thisdate = e[0].date()
        thistime = e[0].time()
        if thisdate == lastdate:
            continue

        lastdate = thisdate
        # do something with the data we have
        #print('   ', thisdate, '-', e[1], 'used out of', lclSize)
        thisUsed = e[1]
        if thisUsed != lastUsed:
            delta = thisUsed - lastUsed
            pct = (delta / lclSize) * 100

            if pct > variance: # current hard-coded variance
                event_list.append(str(thisdate) + ' - ' + humanize(e[1]) + \
                        ' used out of ' + humanize(size) + name + \
                        f' (+{pct:.1f}%, up from ' + humanize(last_e1) + ')')
            elif pct < -variance:
                event_list.append(str(thisdate) + ' - ' + humanize(e[1]) + \
                        ' used out of ' + humanize(size) + name + \
                        f' ({pct:.1f}%, down from ' + humanize(last_e1) + ')')

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
#        if thisUsed != lastUsed:
        if thisUsed > variance:
            event_list.append(str(thisdate) + ' - usage: ' + str(thisUsed))

        lastUsed = thisUsed

# ----------------------------------------------------------------------------
# analyze(sysname, sysdata, switches):
# ----------------------------------------------------------------------------
def analyze(sysname, sysdata, switches):
    """ Look for entries to print
        sysname  is a string of the system we're investigating
        sysdata  is a dictionary, with sysname as the key
        switches is a tuple of Booleans:
            switches[0] = show_events
            switches[1] = show_disk
            switches[2] = show_mem
            switches[3] = show_ping
    """

    global oneday   # find in utils.py
    global event_list   # final output list

    event_list = []     # start fresh
    variance = 19.9 # default variance

# project started 2020-01-03:
#    nexttime = date(2020,1,3)
    nextdate = date(2019, 1, 2)
    lastdate = date(2019, 1, 2)
    thisdate = date(2019, 1, 3)

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
    for sysptr in datedEntries: # sysptr is a System object

        # --- uptime entries:
        entries = sysptr.get_entries('uptime')
        for e in entries:
            thisdate = e[0].date()
            thistime = e[0].time()
            if thisdate == lastdate:
                continue

            lastdate = thisdate

            if thisdate != nextdate:
                if nextdate != date(2019,1,2):
                    event_list.append(str(thisdate) + ' - unexpected datestamp, expected: ' + str(nextdate))
                else:
                    nextdate = thisdate

            nextdate = thisdate + oneday

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
                event_list.append (str(rebootdate.date()) + ' - Rebooted @ ' + str(rebootdate.time()))
                pass

        # --- load entries:
        entries = sysptr.get_entries('load')
        sp = sysptr.get_component('load')
        analyze_load(5.0, sp['entries'])

        # --- Memory entries:
        entries = sysptr.get_entries('Mem')
        sp = sysptr.get_component('Mem')
        chk4variant(sp['size'], 10.0, entries, 'Mem')
        if switches[2] == True:
            print('Memory (' + humanize(sp['size']) + '):')
            printminmaxavg(entries)
            print()

        # --- Swap entries:
        entries = sysptr.get_entries('Swap')
        sp = sysptr.get_component('Swap')
        chk4variant(sp['size'], 10.0, entries, 'Swap')
        if switches[2] == True:
            print('Swap (' + humanize(sp['size']) + '):')
            printminmaxavg(entries)
            print()

        # --- Ping entries:
        if switches[3] == True:
            entries = sysptr.get_entries('Ping')
            print('Ping entries:')
            ping_ok = True
            for e in entries:
                thisdate = e[0].date()
                thistime = e[0].time()
                if thisdate == lastdate:
                    continue

                lastdate = thisdate

                # do something with the data we have
                if e[1] != 'OK':
                    print('   ', thisdate, '-', e[1])
                    event_list.append(str(thisdate) + ' - ' + e[1])
                    ping_ok = False

            if ping_ok == True:
                print('    Ping tests all OK')

            print()

        # --- Services entries:
        entries = sysptr.get_entries('Services')
        for e in entries:
            thisdate = e[0].date()
            thistime = e[0].time()
            if thisdate == lastdate:
                continue

            lastdate = thisdate

            # do something with the data we have
            if e[1][0] != 'OK':
                tmpstr = str(thisdate) + ' - ' + e[1][0] + '\n'
                if type(e[1]) == type([]):
                    y = e[1]
                    for x in y[1:]:
                        tmpstr += '             ' + x + '\n'
                event_list.append(tmpstr)

        # --- Disk entries:
        disklist = sysptr.get_dskkeys()
        for disk in disklist:
            lcldisksize = sysptr.get_dsksize(disk)
            entries = sysptr.get_entries(disk)
            if entries != None:

                # - scan for changes >20% of current usage
                chk4variant(lcldisksize, 20.0, entries, disk)

                # - show min, max, average daily usage
                if switches[1] == True:
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

    event_list.sort()
    if switches[0] == True:
        print('Events:')
        print()
        print(event_list[0][:13] + 'Logging starts')
        for x in event_list:
            print(x)
        print()

    pass

# EOF:
