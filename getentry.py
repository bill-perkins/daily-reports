# getentry.py

# ----------------------------------------------------------------------------
# getEntry(inpdata, index, maxindex)
# ----------------------------------------------------------------------------
def getEntry(inpdata, index, maxindex):
    """ Bring in lines from current index, until we see '----'.
            inpdata:  list of lines from getContent()
            index:    line # we start processing at
            maxindex: last line index of inpdata

        returns:
            nextline: next line to process
            outlist:  list of lines in this entry
    """

    nextline = index
    outlist = []

    while nextline < maxindex and inpdata[nextline][0:4] != '----':
        outlist.append(inpdata[nextline])
        nextline += 1

    return nextline + 1, outlist

# EOF:
