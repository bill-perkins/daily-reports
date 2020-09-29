# analyze.py
#
# this version replaces the original analyze.py and disk_analyze.py
#

from datetime import date
from datetime import timedelta
from statistics import mean

from utils import humanize, oneday

# ----------------------------------------------------------------------------
# printminmaxavg(entries)
# ----------------------------------------------------------------------------
def printminmaxavg(entries):
    """ Print the minimum, maximum, average, starting usage, and ending usage
    """
    values   = [int(e[1]) for e in entries]
    min_used = min(values)
    max_used = max(values)
    max_used_entry = entries[values.index(max_used)]
    min_used_entry = entries[values.index(min_used)]
    avg_used = mean(values)
    havg = humanize(avg_used)

    print('     started:', humanize(entries[0][1]), 'on', entries[0][0].date())
    print('   currently:', humanize(entries[-1][1]), 'on', entries[-1][0].date())
    print('    min used:', humanize(min_used), 'on', min_used_entry[0].date())
    print('    max used:', humanize(max_used), 'on', max_used_entry[0].date())
    print('    avg used:', havg)
    pass

# ----------------------------------------------------------------------------
# chk4variant(size, variance, entries)
# ----------------------------------------------------------------------------
def chk4variant(size, variance, entries):
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
        #print('   ', thisdate, '-', e[1], 'used out of', lclSize)
        thisUsed = e[1]
        if thisUsed != lastUsed:
            delta = thisUsed - lastUsed
            pct = (delta / lclSize) * 100

            if pct > variance: # current hard-coded variance
                print('   ', \
                        thisdate, '-', humanize(e[1]), 'used out of', humanize(size), \
                        f'(+{pct:.1f}%, up from', humanize(last_e1) + ')')
            elif pct < -variance:
                print('   ', \
                        thisdate, '-', humanize(e[1]), 'used out of', humanize(size), \
                        f'({pct:.1f}%, down from', humanize(last_e1) + ')')

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
        # do something with the data we have
        thisUsed = float(e[1][0])
        if thisUsed != lastUsed:
            if thisUsed > variance:
                print('   ', thisdate, '- usage:', thisUsed)

            lastUsed = thisUsed

# ----------------------------------------------------------------------------
# analyze(sysname, sysdata):
# ----------------------------------------------------------------------------
def analyze(sysname, sysdata):
    """ Look for changing or entries and print them
    """

    global oneday
    variance = 19.9
# project started 2020-01-03:
#    nexttime = date(2020,1,3)
    nextdate = date(2019, 1, 2)
    lastdate = date(2019, 1, 2)
    thisdate = date(2019, 1, 3)

    datedEntries = sysdata[sysname]
    if len(datedEntries) == 0:
        print('no entries for', sysname)
        return

    print('# ----------------------------------------------------------------------------')
    print('Analyzing system', sysname + ':')
    print()

    # --- here we have something completely different:
    # to start, we have three keys: name, uptime, load:
    for sysptr in datedEntries:
        print(sysptr.name)
        for component in sysptr.get_keys():
            entries = sysptr.get_entries(component)
            compstr = '\'' + component + '\':'
            if type(entries) == type([]):
                print(compstr.ljust(14), len(entries), 'entries')
            else:
                print(compstr, '=', entries)

        print()

        # --- uptime entries:
        entries = sysptr.get_entries('uptime')
        print('Uptime entries:')
        for e in entries:
            thisdate = e[0].date()
            thistime = e[0].time()
            if thisdate == lastdate:
                continue

            lastdate = thisdate

            if thisdate != nextdate:
                if nextdate != date(2019,1,2):
                    print('   ', thisdate, '- unexpected datestamp, expected:', nextdate)
                else:
                    nextdate = thisdate
                    print('   ', thisdate, '- Logging starts')

            nextdate = thisdate + oneday

            uptime = e[1]
            if 'days,' not in uptime and 'day,' not in uptime:
                # means that we rebooted less than a day ago,
                # so see if we can figure out when we did reboot:
                reboottime = uptime[0].rstrip(',')
                lclhours, lclminutes = reboottime.split(':')
                ago = timedelta(hours = int(lclhours), minutes = int(lclminutes))
                rebootdate = e[0] - ago
                print ('   ', rebootdate.date(), '- Rebooted @', rebootdate.time())
                pass

        print()

        # --- load entries:
        entries = sysptr.get_entries('load')
        print('Load entries:')
        sp = sysptr.get_component('load')
        analyze_load(5.0, sp['entries'])
        print()

        # --- Memory entries:
        entries = sysptr.get_entries('Mem')
        print('Memory entries:')
        sp = sysptr.get_component('Mem')
        chk4variant(sp['size'], 10.0, entries)
        printminmaxavg(entries)
        print()

        # --- Swap entries:
        entries = sysptr.get_entries('Swap')
        print('Swap entries:')
        sp = sysptr.get_component('Swap')
        chk4variant(sp['size'], 10.0, entries)
        printminmaxavg(entries)

        print()

        # --- Ping entries:
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
                ping_ok = False

        if ping_ok == True:
            print('    Ping tests all OK')

        print()

        # --- Services entries:
        entries = sysptr.get_entries('Services')
        print('Service entries:')
        for e in entries:
            thisdate = e[0].date()
            thistime = e[0].time()
            if thisdate == lastdate:
                continue

            lastdate = thisdate

            # do something with the data we have
            if e[1][0] != 'OK':
                print('   ', thisdate, '-', e[1][0])
                if type(e[1]) == type([]):
                    y = e[1]
                    for x in y[1:]:
                        print(''.rjust(16), x)
                print()

        print()

        # --- Disk entries:
        disklist = sysptr.get_dskkeys()
        print('Filesystems:', disklist)
        print()

        for disk in disklist:
            lcldisksize = sysptr.get_dsksize(disk)
            entries = sysptr.get_entries(disk)
            if entries != None:
                print("'{}' entries:".format(disk))

                # - scan for changes >20% of current usage
                chk4variant(lcldisksize, 20.0, entries)
                print()

                # - get min, max, average daily usage
                printminmaxavg(entries)
                print()
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

        pass

# EOF:
