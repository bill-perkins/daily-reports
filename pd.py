#!/usr/bin/env python3
#
# pd.py- process daily.log
# simple script to take daily.log and convert to a dictionary,
# do some analysis of the data
#

# some standard python stuff
import sys
import os

## for debugging:
#import pprint
#pp = pprint.PrettyPrinter(indent=2, width=160)

## if we do this, we have to qualify the functions
## in utils: i.e. utils.humanize(n)
#import utils
#
## so instead, we do this:
## (imports result in .pyc files)
#from utils import *

curSysname = ''              # Global current system name from logfile
iam = sys.argv[0]            # Global program name

from process import *
from analyze import *

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
if __name__ == '__main__':

    if len(sys.argv) == 1:
        arglist = ['daily.log']
    else:
        arglist = sys.argv[1:]

    for inpfile in arglist:
        process(inpfile) # process() updates global allSystems{}

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
