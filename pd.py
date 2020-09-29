#!/usr/bin/env python3
#
# newprocesstest.py- process daily.log
# simple script to take daily.log and convert to a dictionary,
# then do some analysis of the data
#

# some standard python stuff
import sys
import os

## for debugging:
#import pprint
#pp = pprint.PrettyPrinter(indent=2, width=160)

iam = sys.argv[0]           # Global program name
outname = ''                # Global output name

from process import *
from analyze import *

# ----------------------------------------------------------------------------
# usage()
# ----------------------------------------------------------------------------
def usage():
    print('Usage:', iam, '[-? | -h | --help] list_of_logfiles')
    print('list_of_logfiles defaults to daily.log.')
    print()

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    allSystems = {}             # all the system data

    iam = sys.argv.pop(0)       # Global program name

    if len(sys.argv) > 0:       # check args
        # are they looking for help?
        if sys.argv[0] == '-?' or sys.argv[0] == '-h' or sys.argv[0] == '--help':
            usage()
            sys.exit(0)

        # do we have any args left?
        if len(sys.argv) > 0:
            # put new switches here:
            #
            # any switch we don't recognize:
            if sys.argv[0].startswith('-'):
                usage()
                sys.exit(1)

    # did they give us any files to process?
    if len(sys.argv) == 0:
        arglist = ['daily.log'] # use default
    else:
        arglist = sys.argv[:]   # or use what they give us

    # process input files:
    for inpfile in arglist:     # go through given files
        sysname, entries = process(inpfile)
        if sysname != None:
            allSystems[sysname] = entries

    print()

    # display list of systems we found:
    syslist = list(allSystems)
    if len(syslist) > 1:
        print('Systems:')
        for sysname in sorted(syslist):
            print("    " + sysname)

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
