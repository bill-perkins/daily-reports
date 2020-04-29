#!/usr/bin/env python
#
# fixdaily.py: stolen from std.py, the 'standard' python program

import os
import sys
import platform

## pretty-print a dictionary:
#import pprint # for development
# pp = pprint.PrettyPrinter(indent=2, width=160)
# print "dictionary:"
# print
# pp.pprint(dictionary)
# print

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """bring the contents of the given input file into a list,
       and return the list.
       filename: name of the file we're reading
       returns:  list of lines from given file
    """

    output = []

    # open up the new file, bring it in as a list:
    try:
        with open(filename, "r") as inpfile:
            output = inpfile.readlines()

    except IOError as err:
        print "getContent(): Couldn't open file " + filename + ": " + str(err)
#        sys.exit(1)

    return output

# ----------------------------------------------------------------------------
# main() part of the program:
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    """Do something
    """
    argc = len(sys.argv)
    iam  = sys.argv[0]

    hostname = platform.node()

    if argc == 1:
        print iam + ": usage:", iam, "inputfile"
        sys.exit(1)

    inplines = getContent(sys.argv[1])
    starters = [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]
    for line in inplines:
        if line[0:3] in starters:
            print hostname + ": " + line.strip()
        else:
            print line.strip()


# ----------------------------------------------------------------------------
# 
# ----------------------------------------------------------------------------

# EOF:
