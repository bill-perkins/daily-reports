# newprocess.py
# imported by pd.py
#
# Take a given log file and return the system name,
# along with all the dated entries in a dictionary
#

import sys
from collections import deque

import lclvars

from utils import *
from parseentry import *

# ----------------------------------------------------------------------------
# getContent(filename)
# ----------------------------------------------------------------------------
def getContent(filename):
    """ Bring the contents of the given input file into a list,
        and return the list.
        filename: name of the file we're processing (daily.log)
        returns:  deque of lines from given filename;
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

# ----------------------------------------------------------------------------
# process(logfile)
# ----------------------------------------------------------------------------
def process(logfile):
    """ Take a given log file and return the system name,
        along with all the dated entries in a dictionary
    """

    print('processing log file:', logfile)

# EOF:
