#!/usr/bin/env python3
#
# pd.py- process daily.log
# simple script to take daily.log and convert to a dictionary,
# and do some analysis of the data
#

# some standard python stuff
import sys
import os

## for debugging:
#import pprint
#pp = pprint.PrettyPrinter(indent=2, width=160)

iam = sys.argv[0]           # Global program name

from process import *
from analyze import *

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    allSystems = {}         # all the system data

    if len(sys.argv) == 1:
        arglist = ['daily.log'] # use default
    else:
        arglist = sys.argv[1:]  # use what they give us

    for inpfile in arglist:     # go through given files
        sysname, entries = process(inpfile)
        if sysname != None:
            allSystems[sysname] = entries

    print()

    # display list of systems we found:
    syslist = list(allSystems)
    if len(syslist) > 1:
        print('Systems:')
        for line in syslist:
            print("    " + line)

        print()

    # analyze the systems:
    if len(syslist) > 0:
        for sysname in sorted(syslist):
            analyze(sysname, allSystems)

        print()

##------------------------------------------------------------------------------
## pretty-print the resulting dictionary:
#print('allSystems:')
#print()
#pp.pprint(allSystems)
#print()

# ----------------------------------------------------------------------------
#
# ----------------------------------------------------------------------------

# EOF:
