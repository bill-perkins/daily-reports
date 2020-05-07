#!/usr/bin/env python3
#
# fixdaily.py: stolen from std.py, the 'standard' python program

import platform

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
#        sys.exit(1)

    return output

# ----------------------------------------------------------------------------
# main() part of the program:
# ----------------------------------------------------------------------------
if __name__ == '__main__':
    """Do something
    """

    hostname = platform.node()

    inplines = getContent('daily.log')
    starters = [ 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' ]
    for line in inplines:
        if line[0:3] in starters:
            print(hostname + ": " + line.strip())
        else:
            print(line.strip())


# ----------------------------------------------------------------------------
# 
# ----------------------------------------------------------------------------

# EOF:
