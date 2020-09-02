# analyze.py
#

from datetime import date

from analyze_disk import *
from utils import *

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
    nexttime = date(2020,1,3)

    datedEntries = sysdata[sysname]
    if len(datedEntries) == 0:
        print('no entries for', sysname)
        return

    print('# ----------------------------------------------------------------------------')
    print('Analyzing system', sysname + ':')
    print()

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
    # make sorted list of dates:
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
                    invariants[key] = curval # set 'was' values
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

# EOF:
