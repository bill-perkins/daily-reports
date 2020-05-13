# get_avg

from statistics import mean

from utils import *

# ----------------------------------------------------------------------------
# get_avg()
# ----------------------------------------------------------------------------
def get_avg(sysname, which_disk):
    print ('Averages:')
    total = []
    used  = []
    avail = []
    usep  = []

    datedEntries = allSystems[sysname]
    entry_dates = sorted(datedEntries)
    entry_dates.pop(0) # get rid of that annoying blank entry at the start

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

        total.append(t)
        used.append(u)
        avail.append(a)
        usep.append(p)

    used_avg  = mean(used)
    avail_avg = mean(avail)
    usep_avg  = mean(usep)

    print('used avg  :', humanize(used_avg))
    print('avail avg :', humanize(avail_avg))
    print('pct avg   :', str(round(usep_avg, 1)) + '%')
    print()

# EOF:
