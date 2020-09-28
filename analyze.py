# analyze.py
#

from datetime import date
from datetime import timedelta

from analyze_disk import *
from utils import *

# ------------------------------------------------------------------------
# dHumanize(number_string)
# ------------------------------------------------------------------------
def dHumanize(nstr):
    """
    """

    if 'K' in nstr:
        n = float(nstr.rstrip('K'))
        n *= 1024
        return n

    if 'M' in nstr:
        n = float(nstr.rstrip('M'))
        n *= 1024
        n *= 1024.0
        return n

    if 'G' in nstr:
        n = float(nstr.rstrip('G'))
        n *= 1024
        n *= 1024
        n *= 1024.0
        return n

    if 'T' in nstr:
        n = float(nstr.rstrip('T'))
        n *= 1024
        n *= 1024
        n *= 1024
        n *= 1024.0
        return n

    # assume an 'M' was implied:
    n = float(nstr)
    return n * 1024 * 1024

# ----------------------------------------------------------------------------
# chk4variant(size, variance, entries)
# ----------------------------------------------------------------------------
def chk4variant(size, variance, entries):
    """
    """
    lastUsed = 0
    last_e1 = '0'
    lastdate = date(2019, 1, 2)

    lclSize = dHumanize(size)

    for e in entries:
        thisdate = e[0].date()
        thistime = e[0].time()
        if thisdate == lastdate:
            continue

        lastdate = thisdate
        # do something with the data we have
        #print('   ', thisdate, '-', e[1], 'used out of', lclSize)
        thisUsed = dHumanize(e[1])
        if thisUsed != lastUsed:
            delta = thisUsed - lastUsed
            pct = (delta / lclSize) * 100

            if pct > variance: # current hard-coded variance
                print('   ', \
                        thisdate, '-', e[1], 'used out of', size, \
                        f'(+{pct:.1f}%, up from', last_e1 + ')')
            elif pct < -variance:
                print('   ', \
                        thisdate, '-', e[1], 'used out of', size, \
                        f'({pct:.1f}%, down from', last_e1 + ')')

            lastUsed = thisUsed
            last_e1  = e[1]


# ----------------------------------------------------------------------------
# analyze_load(variance, entries):
# ----------------------------------------------------------------------------
def analyze_load(variance, entries):
    """
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
    """ Look for changing immutable values.
        Immutable values are set by the first log entry processed.
        input: sysdata is a dictionary of sysname: datedEntries
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
        print(len(entries), 'uptime entries:')
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
        print(len(entries), 'Load entries:')
        sp = sysptr.get_component('load')
        analyze_load(5.0, sp['entries'])
        print()

        # --- Memory entries:
        entries = sysptr.get_entries('Mem')
        print(len(entries), 'Memory entries:')
        sp = sysptr.get_component('Mem')
        chk4variant(sp['size'], 10.0, entries)

        print()

        # --- Swap entries:
        entries = sysptr.get_entries('Swap')
        print(len(entries), 'Swap entries:')
        sp = sysptr.get_component('Swap')
        chk4variant(sp['size'], 10.0, entries)

        print()

        # --- Ping entries:
        entries = sysptr.get_entries('Ping')
        print(len(entries), 'Ping entries:')
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
        print(len(entries), 'Service entries:')
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
                        print('-'.rjust(16), x)

        print()

        # --- Disk entries:
        disklist = sysptr.get_dskkeys()
        print('disklist:', disklist)
        print()

        for disk in disklist:
            lcldisksize = sysptr.get_dsksize(disk)
            entries = sysptr.get_entries(disk)
            if entries != None:
                print(len(entries), "'{}' entries:".format(disk))

                # - scan for changes >20% of current usage
                chk4variant(lcldisksize, 20.0, entries)

                # - get min, max, average daily usage

                print()
        print()

        # --- Other entries:
        entries = sysptr.get_entries('<entry>')
        if entries != None:
            print(len(entries), '<entry> entries:')
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
