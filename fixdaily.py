#!/usr/bin/env python3
#
# fixdaily.py: stolen from std.py, the 'standard' python program

import platform
import os
import sys

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
        print("getContent(): Couldn't open file " + filename + ": " + str(err))

    return output

# ----------------------------------------------------------------------------
# main() part of the program:
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    """Do something
    """

    iam = sys.argv.pop(0)

    if len(sys.argv) != 2:
        print(f'usage: {iam} logfile hostname_to_use')
        sys.exit(1)

    logfile  = sys.argv[0]
    hostname = sys.argv[1]

    inplines = getContent(logfile)

    starters = [ 'Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ', 'Sun ' ]
    for line in inplines:
        if line[0:4] in starters:
            print(hostname + ": " + line.strip())
        else:
            print(line.rstrip())


# ----------------------------------------------------------------------------
# 
# ----------------------------------------------------------------------------

# EOF:
