# get_chg.py

from utils import *

# ----------------------------------------------------------------------------
# get_chg(sysname which_disk, variance)
# ----------------------------------------------------------------------------
def get_chg(sysname, which_disk, variance = 0.21):
    print('Variances of >', str(variance * 100) + '%')
    datedEntries = allSystems[sysname]
    entry_dates = sorted(datedEntries)
    entry_dates.pop(0) # get rid of that annoying blank entry at the start
    tripped = False

    #---------------------------------------------------------------------
    # analyze used v used_avg:
    # grab logs in date order:
    was = 0
    for datestamp in entry_dates:
        # entry is the dictionary for this datestamp
        entry = datedEntries[datestamp]

        try:
            t, u, a, p = entry[which_disk]
        except KeyError as err:
            continue # we already know it's missing, go for the next

        if was == 0:
            was = p
        else:
            diff = abs(was - p)
            if diff > 0:
                if diff > was * variance:
                    print(datestamp, which_disk, 'usage:', str(int(p)) + '%', 'was:', str(int(was)) + '%')
                    tripped = True

                was = p

    if tripped == False:
        print('(none)')

    print()

# EOF:
