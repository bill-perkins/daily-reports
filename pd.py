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
    """ Show how to use this program.
    """
    print('Usage:', iam, '[-edmp] [-h] list_of_logfiles')
    print('        -e show events')
    print('        -d basic disk analysis')
    print('        -m basic memory/swap analysis')
    print('        -p show ping test results')
    print('        -h show this message')
    print('        switches default to on.')
    print('list_of_logfiles defaults to ./daily.log.')
    print()

# ----------------------------------------------------------------------------
# main() part of the program
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    allSystems = {}             # all the system data
    show_events = True
    show_disk   = True
    show_mem    = True
    show_ping   = True

    iam = sys.argv.pop(0)       # Global program name

    if len(sys.argv) > 0:       # check args
        if sys.argv[0].startswith('-'):
            show_events = False # turn
            show_disk   = False # off
            show_mem    = False # all the
            show_ping   = False # switches

        # turn on the ones they really want:
        while len(sys.argv) > 0 and sys.argv[0].startswith('-'):
            sw = sys.argv.pop(0)
            if 'e' in sw:
                show_events = True

            if 'd' in sw:
                show_disk   = True

            if 'm' in sw:
                show_mem    = True

            if 'p' in sw:
                show_ping   = True

            if 'h' in sw:
                usage()
                sys.exit(1)

            continue

            # any switch we don't recognize, ignore

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
        switches = (show_events, show_disk, show_mem, show_ping)
        for sysname in sorted(syslist):
            analyze(sysname, allSystems, switches)

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
