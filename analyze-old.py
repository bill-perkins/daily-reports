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
    last_e1 = '0'
    lastdate = date(2019, 1, 2)

    for e in entries:
        thisdate = e[0].date()
        thistime = e[0].time()
        if thisdate == lastdate:
            continue

        lastdate = thisdate
        # do something with the data we have
        #print('   ', thisdate, '-', e[1], 'used out of', lclSize)
        thisUsed = float(e[1][0])
        if thisUsed != lastUsed:
            if thisUsed > variance:
                print('   ', thisdate, '- usage:', thisUsed)

#            delta = thisUsed - lastUsed
#            pct = (delta / lclSize) * 100
#            if delta == 0:
#                pct = 0.0
#            elif delta < 0:
#                pct = (delta / lastUsed) * 100
#            else:
#                pct = (delta / thisUsed) * 100
#
#            if pct > variance: # current hard-coded variance
#                print('   ', \
#                        thisdate, '-', str(e[1][0]), 'used', \
#                        f'(+{pct:.1f}%, up from', str(last_e1[0]) + ')')
#            elif pct < -variance:
#                print('   ', \
#                        thisdate, '-', str(e[1][0]), 'used', \
#                        f'({pct:.1f}%, down from', str(last_e1[0]) + ')')

            lastUsed = thisUsed
            last_e1  = e[1]

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

    """
    # invariants dictionary, start fresh for each system:
    invariants = { \
            'Uptime':    '', \
            '/':         [0.0, 0.0, 0.0, 0.0], \
            '/opt/sas':  [0.0, 0.0, 0.0, 0.0], \
            '/sasdata':  [0.0, 0.0, 0.0, 0.0], \
            '/sastmp':   [0.0, 0.0, 0.0, 0.0], \
            'Swap':      [0.0, 0.0, 0.0, 0.0], \
            'Mem':       [0.0, 0.0, 0.0, 0.0], \
            'ping test': '',  \
            'services':  '',  \
            }

    disk_invariants = ['/', '/opt/sas', '/sasdata', '/sastmp', 'Swap']
    """

    # make sorted list of dates:

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
        print(len(entries), 'load entries:')
        sp = sysptr.get_component('load')
        analyze_load(1.0, sp['entries'])
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

    """
    # Original code:
    entry_dates = sorted(datedEntries)

    # analyze each dated entry:
    for datestamp in entry_dates:
        if datestamp == '':
            continue

        # entry is the log dictionary for this datestamp:
        entry = datedEntries[datestamp]

        # get a date object for this datestamp:
        thisdate = date(int(datestamp[0:4]), \
                int(datestamp[5:7]), \
                int(datestamp[8:10]))   # year, month, day

        # complain if we see something unexpected:
        if thisdate != nexttime:
            if str(nexttime) != '2020-01-03':
                print(thisdate, 'expected datestamp:', nexttime)
            else:
                nexttime = thisdate
                print(thisdate, 'Logging starts')

        # set nexttime to thisdate plus 1 day:
        nexttime = thisdate + oneday

        # Search for changes to invariant data.
        # When something comes up different, complain about it,
        # then change the invariants list to the new value.
        for key, preval in list(invariants.items()):
            try:
                curval = entry[key]
            except KeyError as err:
                continue # key not there? Who cares?

            # we have key and curval, which may be a list:
            if key == 'Uptime':
                # Did we reboot?
                if 'days' not in curval[0]:
                    hm = curval[0].split(':')
                    dTime = timedelta(hours = int(hm[0]), minutes = int(hm[1]))
                    cTime = entry['Datetime'][0]
                    rebooted = cTime - dTime
                    print(rebooted.date(), 'Reboot @', rebooted.time())
                continue

            # flag first appearance:
            if key == 'services' and invariants['services'] == '':
                invariants['services'] = 'OK'
                print(thisdate, 'first appearance of services check')
                continue

            # flag first appearance:
            if key == 'ping test' and invariants['ping test'] == '':
                invariants['ping test'] = 'OK'
                print(thisdate, 'first appearance of ping test')
                continue

            # services:
            if key == 'services' and curval[0] != 'OK':
                # curval is 'denodo services:'
                # print('key: services, curval:', curval)
                downlist = entry['DOWN']
                dLines = downlist[0]
                if len(dLines) == 0:
                    continue
                # we don't care to hear about sas-viya-dmtransformservices-default:
                if len(dLines) == 1 and dLines[0] != 'sas-viya-dmtransformservices-default':
                    print(thisdate, '(1) service was DOWN:')
                    print('          ', dLines[0])
                    print()
                else:
                    print(thisdate, '(' + str(len(dLines)) + ') services were DOWN:')
                    for dLine in dLines:
                        print('          ', dLine)
                    print()

                # final print to separate downed services:
                continue

            # see if the key is one of the disks:
            # preval is from invariants
            # curval is what we are currently reading
            # leave sastmp out of it, it changes too much:
            if key in disk_invariants:
                if preval[0] == 0.0:
                    invariants[key] = curval # set 'previous' values
                    continue

                if len(curval) > 3:
                    if curval[3] > 89.0:
                        print(thisdate, key, 'usage over 89%:', str(curval[3]) + '%')

                if key != '/sastmp':
                    # look for size change (1st in list):
                    size_change = abs(preval[0] - curval[0])
                    if size_change != 0:
                        print(thisdate, key.ljust(8), "size change from", preval[0], "to", curval[0])
                        preval[0] = curval[0]

                    # look for usage change:
                    used_was = round(preval[1] / preval[0] * 100, 1)    # % used was
                    used_is  = round(curval[1] / curval[0] * 100, 1)    # % used is
                    if 20 < abs(used_is - used_was):                    # 20% or greater
                        chgsin = used_is - used_was                     # so we can do + or -
                        change = abs(chgsin)                            # get the actual change
                        if chgsin < 0:
                            chgsin = -1
                        else:
                            chgsin = 1

                        change = round(change, 1)               # round it up, just 1 digit past decimal pt
                        print(thisdate, 'usage change:', \
                                key.ljust(8) + (str(chgsin * change) + '%').rjust(8), end='')
                        print(' from:', (str(used_was) + '%').rjust(6), \
                                'to:',  (str(used_is)  + '%').rjust(6))

                preval[1] = curval[1]   # set previous preval to current value

            else:   # it's not in disk_invariants:
                if preval == [0.0, 0.0, 0.0, 0.0]:
                    pass
                elif preval != curval[0]:
                    if key == 'ping test':
                        print(thisdate, 'ping test:')
                        print(repr(curval[0]))
                        continue # skip changing the output value of the ping test
                    else:
                        print(thisdate, key + \
                                ": change from '" + str(preval) + \
                                "' to '" + str(curval[0]) + "'")

                invariants[key] = curval[0]
                continue

    print(datestamp, 'Final entry')
    print()

    # basic analysis on each of the disks:
    if lclvars.outfile != None:
        print('filesystem, size, avg(used), avg(avail), avg(% used), start date, used, avail, % used, end date, used, avail, %used, max usage', file = lclvars.outfile)

    for key in disk_invariants:
        analyze_disk(sysdata, sysname, key, 0.19)

    # final print to separate system reports:
    print()
    """

# EOF:
