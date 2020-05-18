# analyze_disk.py

from statistics import mean

from utils import *

# ----------------------------------------------------------------------------
# get_avg()
# ----------------------------------------------------------------------------
def get_avg(systems, sysname, which_disk):
    print ('    Averages:')
    total = []
    used  = []
    avail = []
    usep  = []

    datedEntries = systems[sysname]
    entry_dates = sorted(datedEntries)
#    if len(entry_dates[0]) == 0:
#        entry_dates.pop(0) # get rid of that annoying blank entry at the start

    #---------------------------------------------------------------------
    for datestamp in entry_dates:
        # entry is the dictionary for this datestamp
        entry = datedEntries[datestamp]

        try:
            t, u, a, p = entry[which_disk]
        except KeyError as err:
            print('*** missing disk entry for', which_disk, 'on:', datestamp)
            print()
            continue # continue anyway
        except ValueError as err:
            t, u, a = entry[which_disk]
            p = 0

        total.append(t)
        used.append(u)
        avail.append(a)
        usep.append(p)

    used_avg  = mean(used)
    avail_avg = mean(avail)
    usep_avg  = mean(usep)

    print('used avg  :'.rjust(19), humanize(used_avg).rjust(6))
    print('avail avg :'.rjust(19), humanize(avail_avg).rjust(6))
    print('pct avg   :'.rjust(19), str(round(usep_avg, 1)).rjust(5) + '%')
    print()

# ----------------------------------------------------------------------------
# analyze_disk()
# ----------------------------------------------------------------------------
def analyze_disk(systems, sysname, which_disk, variance = 0.21):
    """Analyze the disk entries in systems{}
    """

    print('Analyzing',  which_disk, 'file system of', sysname + ':')
    print()

    get_avg(systems, sysname, which_disk)

    datedEntries = systems[sysname]
    entry_dates = sorted(systems[sysname])

    #---------------------------------------------------------------------
    # spit out where we started, where we ended:
    print('    Start and end values:')

    logStart = entry_dates[1]
    entry = datedEntries[logStart]
    if len(entry[which_disk]) == 3:
        t, u, a = entry[which_disk]
        p = 0
    else:
        t, u, a, p = entry[which_disk]
    print('       ', logStart, which_disk, "started at:", humanize(u).rjust(6), \
            'used,', humanize(a).rjust(6), 'available,', str(p) + '% used')

    logEnds  = entry_dates[-1]
    entry = datedEntries[logEnds]
    if len(entry[which_disk]) == 3:
        t, u, a = entry[which_disk]
        p = 0
    else:
        t, u, a, p = entry[which_disk]
    print('       ', logEnds,  which_disk, "ended at:  ", humanize(u).rjust(6), \
            'used,', humanize(a).rjust(6), 'available,', str(p) + '% used')

# EOF:
