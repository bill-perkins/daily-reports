# analyze.py
#

from datetime import date

from analyze_disk import *
from utils import *

# ----------------------------------------------------------------------------
# analyze(systems):
# ----------------------------------------------------------------------------
def analyze(systems):
    """ Look for changing immutable values.
        Immutable values are set by the first log entry processed.
        input: systems is a dictionary of sysname: datedEntries
    """

    global oneday
    variance = 19.9

    # --- analyze each system:
    for sysname, datedEntries in list(systems.items()):
        nexttime = date(2020,1,3)

        print('Analyzing system', sysname + ':')
        print()

        # invariants dictionary, start fresh for each system:
        invariants = {'/':   [0.0, 0.0, 0,0, 0,0], \
                '/opt/sas':  [0.0, 0.0, 0,0, 0,0], \
                '/sasdata':  [0.0, 0.0, 0,0, 0,0], \
                '/sastmp':   [0.0, 0.0, 0,0, 0,0], \
                'Mem':       [0.0, 0.0, 0,0, 0,0], \
                'Swap:':     [0.0, 0.0, 0,0, 0,0], \
                'ping test': '',  \
                'services':  '',  \
                'Uptime':   '' }

        # grab logs in date order:
        entry_dates = sorted(datedEntries)
        if len(entry_dates[0]) == 0:
            entry_dates.pop(0) # get rid of that annoying blank entry at the start

        # analyze each dated entry:
        for datestamp in entry_dates:
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
            for key, value in list(invariants.items()):
                try:
                    val = entry[key]
                except KeyError as err:
                    continue # key not there? Who cares?

                # we have key and val, which may be a list:
                if key == 'Uptime':
                    # Did we reboot?
                    if 'days' not in val[0]:
                        hm = val[0].split(':')
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

                if key == 'services' and val[0] != 'OK':
                    downlist = entry['DOWN']
                    dLines = downlist[0]
                    if len(dLines) == 1:
                        print(thisdate, '1 service was down:')
                        print('          ', dLines[0])
                    else:
                        print(thisdate, len(dLines), 'services were down:')
                        for dLine in dLines:
                            print('          ', dLine)

                    # final print to separate downed services:
                    print()
                    continue

                # see if the key is one of the disks:
                if key in list(invariants)[0:4]:
                    if value == '' or value[0] == 0.0:
                        invariants[key] = val # set 'was' values
                    else:
                        chk_variance(invariants[key], value, variance)

                else:   # we're looking at a different invariant key
                    if value == '' or value == 0.0:
                        pass
                    elif value != val[0]:
                        print(thisdate, key + \
                                ": expected: '" + str(value) + \
                                "', found: '" + str(val[0]) + "'")

                    invariants[key] = val[0]
                    continue

        print(datestamp, 'Final entry')
        print()

        for key in list(invariants)[0:4]:
            analyze_disk(systems, sysname, key, 0.19)
            print()

        # final print to separate system reports:
        print()

# EOF:
