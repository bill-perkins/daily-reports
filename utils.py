# utility functions for this project
import sys

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """ Bring the contents of the given input file into a list,
        and return the list.
        filename: name of the file we're processing (daily.log)
        returns:  reverse() of lines from given filename;
            sys.exit(1) if file not found or permissions error.
    """

    logcontent = []

    # open given filename, bring it in as a list:
    try:
        with open(filename, 'r') as inpfile:
            logcontent = inpfile.readlines()

    except FileNotFoundError as err:
        print('getContent():', str(err))
        sys.exit(1)

    except PermissionError as err:
        print('getContent():', str(err))
        sys.exit(1)

    logcontent.reverse()
    return logcontent

# -----------------------------------------------------------------------------
# humanize(number)- change number to human-readable format
# -----------------------------------------------------------------------------
def humanize(f):
    """ Change a given float to a human-readable format.
    """
    if not isinstance(f, int) and not isinstance(f, float):
        return f

    if f < 1024:
        return str(f) + "B"

    if f < (1024 * 1024):
        return '{:3.1f}'.format(f / 1024.0) + "K"

    if f < (1024 * 1024 * 1024):
        return '{:3.1f}'.format(f / 1024.0 / 1024) + "M"

    if f < (1024 * 1024 * 1024 * 1024):
        return '{:3.1f}'.format(f / 1024.0 / 1024 / 1024) + "G"

    return '{:3.1f}'.format(f / 1024.0 / 1024 / 1024 / 1024) + "T"

# ------------------------------------------------------------------------
# dHumanize(number_string)
# ------------------------------------------------------------------------
def dHumanize(nstr):
    """ Convert a number string with K/M/G/T to a floating-point count
        of bytes.
    """

    if 'K' in nstr:
        n = float(nstr.rstrip('K'))
        return n * 1024

    if 'M' in nstr:
        n = float(nstr.rstrip('M'))
        return n * 1024 * 1024

    if 'G' in nstr:
        n = float(nstr.rstrip('G'))
        return n * 1024 * 1024 * 1024

    if 'T' in nstr:
        n = float(nstr.rstrip('T'))
        return n * 1024 * 1024 * 1024 * 1024

    # assume an 'M' was implied:
    n = float(nstr)
    return n * 1024 * 1024

# EOF:
