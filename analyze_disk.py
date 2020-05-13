from get_avg import *
from utils import *
from get_chg import *

# ----------------------------------------------------------------------------
# analyze_disk()
# ----------------------------------------------------------------------------
def analyze_disk(sysname, which_disk, variance = 0.21):
    """Analyze the disk entries in systems{}
    """

    print('Analyzing',  which_disk, 'file system of', sysname + ':')
    print()

    get_avg(sysname, which_disk)
    get_chg(sysname, which_disk, variance)

    datedEntries = allSystems[sysname]
    entry_dates = sorted(allSystems[sysname])

    #---------------------------------------------------------------------
    # spit out where we started, where we ended:
    print('Start end end values:')

    logStart = entry_dates[1]
    entry = datedEntries[logStart]
    t, u, a, p = entry[which_disk]
    print(logStart, which_disk, "started at:", humanize(u), 'used,', humanize(a), 'available,', str(p) + '% used')

    logEnds  = entry_dates[-1]
    entry = datedEntries[logEnds]
    t, u, a, p = entry[which_disk]
    print(logEnds,  which_disk, "ended at:  ", humanize(u), 'used,', humanize(a), 'available,', str(p) + '% used')

# EOF:
