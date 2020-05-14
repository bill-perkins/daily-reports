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
        arglist = ['daily.log']
    else:
        arglist = sys.argv[1:]

    for inpfile in arglist:
        sysname, entries = process(inpfile)
        allSystems[sysname] = entries

    print()

    # display list of systems we found:
    syslist = list(allSystems)
    print('Systems:')
    for line in syslist:
        print("    " + line)

    print()

    analyze(allSystems)
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
