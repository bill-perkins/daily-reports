# analyze_disk.py
# Analyze a specific disk's entries in systems{}

from statistics import mean

from utils import *

import lclvars

# ----------------------------------------------------------------------------
# get_total_avg()
# ----------------------------------------------------------------------------
def get_total_avg(systems, sysname, which_disk):
    """ Get total average disk usage of a given disk in a given system
    """
    total = []
    used  = []
    avail = []
    usep  = []
    used_avg  = 0.0
    avail_avg = 0.0
    usep_avg  = 0.0
    max_used = 0.0

    datedEntries = systems[sysname]
    entry_dates = sorted(datedEntries)

    #---------------------------------------------------------------------
    for datestamp in entry_dates:
        # entry is the dictionary for this datestamp
        entry = datedEntries[datestamp]

        if which_disk not in entry.keys():
            continue;

        # get total, used, available, percent usage:
        try:
            t, u, a, p = entry[which_disk]
        except ValueError as err:
            t, u, a = entry[which_disk]
            p = 0

        total.append(t)
        used.append(u)
        avail.append(a)
        usep.append(p)

    if len(used) > 0:
        used_avg  = mean(used)
        max_used = max(used)

    if len(avail) > 0:
        avail_avg = mean(avail)

    if len(usep) > 0:
        usep_avg  = mean(usep)

    return used_avg, avail_avg, usep_avg, max_used

# ----------------------------------------------------------------------------
# analyze_disk()
# ----------------------------------------------------------------------------
def analyze_disk(systems, sysname, which_disk, variance = 0.21):
    """ Analyze a specific disk's entries in systems{}
        systems-    data dictionary
        sysname-    key for which system we're analyzing
        which_disk- key for the disk we're anayzing
        variance-   threshold to trigger output
    """
    csvline = ''

    used_avg, avail_avg, usep_avg, max_used = get_total_avg(systems, sysname, which_disk)
    if avail_avg == 0.0:
        return

    datedEntries = systems[sysname]
    entry_dates = sorted(systems[sysname])

    print("Analyzing '" + str(which_disk) + "' file system of", sysname + ':')
    print()

    print ('    Averages:')
    print('used avg  :'.rjust(19), humanize(used_avg).rjust(6))
    print('avail avg :'.rjust(19), humanize(avail_avg).rjust(6))
    print('pct avg   :'.rjust(19), str(round(usep_avg, 1)).rjust(5) + '%')
    print()

    #---------------------------------------------------------------------
    # spit out where we started, where we ended:
    print('    Start and end values:')

    logStart = entry_dates[1]
    entry    = datedEntries[logStart]
    if len(entry[which_disk]) == 3:
        t, u, a = entry[which_disk]
        p = 0
    else:
        t, u, a, p = entry[which_disk]
    print('       ', logStart, which_disk, "started at:", humanize(u).rjust(6), \
            'used,', humanize(a).rjust(6), 'available,', str(p) + '% used')

    csvline = str(which_disk) + ', '
    csvline += humanize(t) + ', '
    csvline += humanize(used_avg) + ', ' + humanize(avail_avg) + ', ' + phumanize(usep_avg) + ', '
    csvline += logStart + ', ' + humanize(u) + ', ' + humanize(a) + ', ' + phumanize(p) + ', '

    logEnds = entry_dates[-1]
    entry   = datedEntries[logEnds]
    if len(entry[which_disk]) == 3:
        t, u, a = entry[which_disk]
        p = 0
    else:
        t, u, a, p = entry[which_disk]
    print('       ', logEnds,  which_disk, "ended at:  ", humanize(u).rjust(6), \
            'used,', humanize(a).rjust(6), 'available,', str(p) + '% used')

    print()
    print('    Size     :', humanize(t).rjust(6))
    print('    Max Used :', humanize(max_used).rjust(6))

    csvline += logEnds + ', ' + humanize(u) + ', ' + humanize(a) + ', ' + phumanize(p) + ', '
    csvline += humanize(max_used) + ', '

    print()

    # filesystem, size, avg(used), avg(avail), avg(% used),
    #   start date, used, avail, % used,
    #   end date, used, avail, %used, max usage:
    if lclvars.outfile != None:
        print(csvline, file = lclvars.outfile)

# EOF:
