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
        input: systems is a dictionary of sysname: datedEntries
    """

    global oneday
    variance = 19.9
    nexttime = date(2020,1,3)

    datedEntries = sysdata[sysname]
    if len(datedEntries) == 0:
        print('no entries for', sysname)
        return

    print('Analyzing system', sysname + ':')
    print()

    # invariants dictionary, start fresh for each system:
    invariants = {'/':   [0.0, 0.0, 0.0, 0.0], \
            '/opt/sas':  [0.0, 0.0, 0.0, 0.0], \
            '/sasdata':  [0.0, 0.0, 0.0, 0.0], \
            '/sastmp':   [0.0, 0.0, 0.0, 0.0], \
            'Mem':       [0.0, 0.0, 0.0, 0.0], \
            'Swap':      [0.0, 0.0, 0.0, 0.0], \
            'ping test': '',  \
            'services':  '',  \
            'Uptime':   '' }

    # make sorted list of dates:
    entry_dates = sorted(datedEntries)

#    if len(entry_dates[0]) == 0:
#        entry_dates.pop(0) # get rid of that annoying blank entry at the start

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
                    print(thisdate, '(1) service was down:')
                    print('          ', dLines[0])
                else:
                    print(thisdate, '(' + str(len(dLines)) + ') services were down:')
                    for dLine in dLines:
                        print('          ', dLine)

                # final print to separate downed services:
                print()
                continue

            # see if the key is one of the disks:
            # value is from invariants
            # val is what we are currently reading
            # leave sastmp out of it, it changes too much:
            if key in list(invariants)[0:3]:
                if value[0] == 0.0:
                    invariants[key] = val # set 'was' values
                else:
                    # look for size change:
                    change = abs(value[0] - val[0])
                    if change != 0.0:
                        print(thisdate, key.ljust(8), "size change from", value[0], "to", val[0])
                        value[0] = val[0]

                    # look for a use% change > variance:
                    change = abs(value[1] - val[1])
                    pct = change / value[1]
                    if pct * 100 > variance:
                        print(thisdate, 'usage change:', key.ljust(8) + \
                                '{:4.1%}: from '.format(pct).rjust(16) + \
                                humanize(value[1]).rjust(6), 'to', humanize(val[1]).rjust(6))
                        value[1] = val[1]

            else:   # we're looking at a different invariant key
                if value == [0.0, 0.0, 0.0, 0.0]:
                    pass
                elif value != val[0]:
                    print(thisdate, key + \
                            ": from '" + str(value) + \
                            "', to '" + str(val[0]) + "'")

                invariants[key] = val[0]
                continue

    print(datestamp, 'Final entry')
    print()

    for key in list(invariants)[0:4]:
        analyze_disk(sysdata, sysname, key, 0.19)
        print()

    # final print to separate system reports:
    print()

# EOF:
