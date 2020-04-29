#!/usr/bin/env python
#
# std.py: 'standard' python program

import os
import sys
import pprint # for development


## pretty-print a dictionary:
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
    print "iam:", iam, "argc:", argc

# ----------------------------------------------------------------------------
# 
# ----------------------------------------------------------------------------

# EOF:
