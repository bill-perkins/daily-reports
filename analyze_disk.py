# analyze_disk.py

from statistics import mean

from utils import *

# ----------------------------------------------------------------------------
# get_avg()
# ----------------------------------------------------------------------------
def get_avg(systems, sysname, which_disk):
    total = []
    used  = []
    avail = []
    usep  = []
    used_avg  = 0.0
    avail_avg = 0.0
    usep_avg  = 0.0

    datedEntries = systems[sysname]
    entry_dates = sorted(datedEntries)

    #---------------------------------------------------------------------
    for datestamp in entry_dates:
        # entry is the dictionary for this datestamp
        entry = datedEntries[datestamp]

        if which_disk in entry.keys():
            try:
                t, u, a, p = entry[which_disk]
            except ValueError as err:
                t, u, a = entry[which_disk]
                p = 0
        else:
            continue;

        total.append(t)
        used.append(u)
        avail.append(a)
        usep.append(p)

    if len(used) > 0:
        used_avg  = mean(used)

    if len(avail) > 0:
        avail_avg = mean(avail)

    if len(usep) > 0:
        usep_avg  = mean(usep)

    return used_avg, avail_avg, usep_avg

# ----------------------------------------------------------------------------
# analyze_disk()
# ----------------------------------------------------------------------------
def analyze_disk(systems, sysname, which_disk, variance = 0.21):
    """Analyze the disk entries in systems{}
    """

    used_avg, avail_avg, usep_avg = get_avg(systems, sysname, which_disk)
    if avail_avg > 0.0: # HACK: if avail_avg is 0, we don't have this disk
        print('Analyzing',  which_disk, 'file system of', sysname + ':')
        print()

        print ('    Averages:')
        print('used avg  :'.rjust(19), humanize(used_avg).rjust(6))
        print('avail avg :'.rjust(19), humanize(avail_avg).rjust(6))
        print('pct avg   :'.rjust(19), str(round(usep_avg, 1)).rjust(5) + '%')
        print()

        datedEntries = systems[sysname]
        entry_dates = sorted(systems[sysname])

        #---------------------------------------------------------------------
        # spit out where we started, where we ended:
        print('    Start and end values:')

        logStart = entry_dates[1]
        entry = datedEntries[logStart]
        if which_disk in entry.keys():
            if len(entry[which_disk]) == 3:
                t, u, a = entry[which_disk]
                p = 0
            else:
                t, u, a, p = entry[which_disk]
            print('       ', logStart, which_disk, "started at:", humanize(u).rjust(6), \
                    'used,', humanize(a).rjust(6), 'available,', str(p) + '% used')

        logEnds  = entry_dates[-1]
        entry = datedEntries[logEnds]
        if which_disk in entry.keys():
            if len(entry[which_disk]) == 3:
                t, u, a = entry[which_disk]
                p = 0
            else:
                t, u, a, p = entry[which_disk]
            print('       ', logEnds,  which_disk, "ended at:  ", humanize(u).rjust(6), \
                    'used,', humanize(a).rjust(6), 'available,', str(p) + '% used')
        print()

# EOF:
