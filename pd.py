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
outname = ''                # Global output name

import lclvars
from process import *
from analyze import *

# ----------------------------------------------------------------------------
# usage()
# ----------------------------------------------------------------------------
def usage():
    print(iam + ': usage:', iam, '[-c <disklog.csv>] [-?] [list of logfiles]')
    print('    -c for a nice .csv disk report.')
    print('    default logfile to process is daily.log.')

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    allSystems = {}             # all the system data

    iam = sys.argv.pop(0)       # Global program name
    if len(sys.argv) > 0:       # check args
        # are the looking for help?
        if sys.argv[0] == '-?':
            usage()
            sys.exit(1)

        # do they want a disk report?
        if sys.argv[0] == '-c':
            sys.argv.pop(0)

            # sanity check:
            if len(sys.argv) == 0:
                usage();
                sys.exit(1)

            # create .csv output file:
            outname = sys.argv.pop(0)
            lclvars.outfile = open(outname, "w")

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

    # close the output file if we had one:
    if lclvars.outfile != None:
        lclvars.outfile.close()

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
