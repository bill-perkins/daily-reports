# analyze_disk.py

from statistics import mean

from utils import *

# ----------------------------------------------------------------------------
# chk_variances(variance)
# ----------------------------------------------------------------------------
def chk_variance(invariants, values, variance):
#    print('disk    :', disk)
#    print('variance:', variance)
#    print('value   :', value[0])
#    print('was     :', value[1])
#    if value[0] != value[1]:
#        print('changed: disk:', disk, 'was:', value[1], 'now:', value[0])
#        print()
    if invariants[0] != values[0]:
        print('size change from:', humanize(invariants[0]), 'to:', humanzie(values[0]))

    if invariants[1] != values[1]:
        pass
    if invariants[2] != values[2]:
        pass
    if invariants[3] != values[3]:
        pass
    pass

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
    if len(entry_dates[0]) == 0:
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

    print('        used avg  :', humanize(used_avg))
    print('        avail avg :', humanize(avail_avg))
    print('        pct avg   :', str(round(usep_avg, 1)) + '%')
    print()

# ----------------------------------------------------------------------------
# get_chg(systems, sysname which_disk, variance)
# ----------------------------------------------------------------------------
def get_chg(systems, sysname, which_disk, variance = 0.21):
    print('    Variances of >', str(variance * 100) + '%')

    datedEntries = systems[sysname]
    entry_dates = sorted(datedEntries)
    if len(entry_dates[0]) == 0:
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
                    print('       ', datestamp, which_disk, \
                            'usage:', str(int(p)) + '%', \
                            'was:', str(int(was)) + '%')
                    tripped = True

                was = p

    if tripped == False:
        print('        (none)')

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
    get_chg(systems, sysname, which_disk, variance)

    datedEntries = systems[sysname]
    entry_dates = sorted(systems[sysname])

    #---------------------------------------------------------------------
    # spit out where we started, where we ended:
    print('    Start and end values:')

    logStart = entry_dates[1]
    entry = datedEntries[logStart]
    t, u, a, p = entry[which_disk]
    print('       ', logStart, which_disk, "started at:", humanize(u), \
            'used,', humanize(a), 'available,', str(p) + '% used')

    logEnds  = entry_dates[-1]
    entry = datedEntries[logEnds]
    t, u, a, p = entry[which_disk]
    print('       ', logEnds,  which_disk, "ended at:  ", humanize(u), \
            'used,', humanize(a), 'available,', str(p) + '% used')

# EOF:
