# newprocess.py
# imported by pd.py
#
# Take a given log file and return the system name,
# along with all the dated entries in a dictionary
#

import sys
import lclvars
from utils import *
from parseentry import *
from systems import System

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
# gather_data()
# ----------------------------------------------------------------------------
def gather_data(lines):
    """ Parse given data, extract useful information:
    """
    sysobjlist = []
    sysnames = []       # list of system names
    sysname  = ''
    sDate    = ''
    sTime    = ''
    newsystem = True    # used to create disk objects in new system entries
    sysobj = None       # current system object

    # main processing loop:
    while len(lines) > 1:
        line = lines.pop()
        if len(line) == 1:
            continue                    # skip blank lines

        ## NOTE: timestamp is found differently
        #if line.startswith('20'):
        #    sDate, sTime = line.rstrip().split()
        #    continue                    # got date and time for this entry
        #
        ## NOTE: system name is found differently
        #if line.startswith('##'):       # we have the system name
        #    sysname = line.split()[1].rstrip(':')
        #    lines.pop()                 # (scrap the headers line)
        #
        #    if sysname in sysnames:     # we have a known system
        #        sysobj = sysobjlist[sysnames.index(sysname)]
        #    else:                       # we have a new system
        #        sysnames.append(sysname)
        #        sysobjlist.append(System(sysname))
        #        sysobj = sysobjlist[-1]
        #        newsystem = True        # add disk objects to this new system
        #        # NOTE: do initial new system processing here

        if 'corp.loca' in line and ' ping ' not in line:
            sysname = line.split(':')[0]

            # sanity check: no hostname = we don't have sysname
            if sysname == '':
                print("can't find hostname in", logfile)
                print('...skipped...')
                print()
                return None, None

            # extract date, time:
            datestr = line.split()[1:]

        # NOTE: parse and process other lines here
        else:
            continue                    # skip lines we know nothing about

#        # NOTE: this is for processing disk usages
#        # get the file system usage lines:
#        rootfsline = lines.pop()
#        sasdatline = lines.pop()
#        sastmpline = lines.pop()
#        optsasline = lines.pop()
#
#        # NOTE: we will want more than just these four, use an fslist[]
#        # create disk objects for this new system:
#        if newsystem == True:
#            # add a Disk object, name and size from parts[]:
#            parts = rootfsline.split()
#            root  = parts[5]
#            size  = int(parts[1])
#            sysobj.add_disk(root, size)
#
#            # add a Disk object, name and size from parts[]:
#            parts = sasdatline.split()
#            sas   = parts[5]
#            size  = int(parts[1])
#            sysobj.add_disk(sas,  size)
#
#            # add a Disk object, name and size from parts[]:
#            parts = sastmpline.split()
#            tmp   = parts[5]
#            size  = int(parts[1])
#            sysobj.add_disk(tmp,  size)
#
#            # add a Disk object, name and size from parts[]:
#            parts = optsasline.split()
#            opt   = parts[5]
#            size  = int(parts[1])
#            sysobj.add_disk(opt,  size)
#
#            newsystem = False  # so we don't do this again
#
#        sysobj.add_usage(root, [sDate, sTime, int(rootfsline.split()[2])])
#        sysobj.add_usage(sas,  [sDate, sTime, int(sasdatline.split()[2])])
#        sysobj.add_usage(tmp,  [sDate, sTime, int(sastmpline.split()[2])])
#        sysobj.add_usage(opt,  [sDate, sTime, int(optsasline.split()[2])])
#
    # NOTE: will also want to return the system name
    #       if this is to work like the original
    return sysname, sysobjlist
    # end gather_data()

# ----------------------------------------------------------------------------
# process(logfile)
# ----------------------------------------------------------------------------
def process(logfile):
    """ Take a given log file and return the system name,
        along with all the dated entries in a dictionary
    """

    print('processing log file:', logfile)
    loglines = getContent(logfile)
    return gather_data(loglines)

# EOF:
