# utility functions for this project
import sys
from datetime import datetime
from datetime import date
from datetime import timedelta

# if a line starts with a day of the week, we want to add the
# hostname to the line.
starters = [ 'Mon ', 'Tue ', 'Wed ', 'Thu ', 'Fri ', 'Sat ', 'Sun ' ]

oneday = timedelta(days = 1) # Global timedelta of one day

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """bring the contents of the given input file into a list,
       and return the list.
       filename: name of the file we're processing (daily.log)
       returns:  list of lines from given file
    """

    logcontent = []

    # open given filename, bring it in as a list:
    try:
        with open(filename, 'r') as inpfile:
            logcontent = inpfile.readlines()

    except FileNotFoundError as err:
        print('getContent():', str(err))
        sys.exit(0)

    except PermissionError as err:
        print('getContent():', str(err))
        sys.exit(0)

    return logcontent

# -----------------------------------------------------------------------------
# humanize(number)- change number to human-readable format
# -----------------------------------------------------------------------------
def humanize(f):
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

# ----------------------------------------------------------------------------
# ms2bytes(s)- change memory/swap values to MB
# ----------------------------------------------------------------------------
def ms2bytes(s):
    return float(s) * 1024 * 1024

# ----------------------------------------------------------------------------
# to_bytes()- change strings with 'G', 'M', 'K', '%' to appropriate numbers
# ----------------------------------------------------------------------------
def to_bytes(s):
    if 'T' in s:
        v = float(s[:-1]) * 1024 * 1024 * 1024 * 1024
    elif 'G' in s:
        v = float(s[:-1]) * 1024 * 1024 * 1024
    elif 'M' in s:
        v = float(s[:-1]) * 1024 * 1024
    elif 'K' in s:
        v = float(s[:-1]) * 1024
    elif '%' in s:
        v = float(s[:-1])
    else:
        v = float(s)

    return v

# EOF:
