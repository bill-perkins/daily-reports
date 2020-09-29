#!/usr/bin/env python3
#
# demonstrate pass-by-value
#

import sys
from datetime import datetime

list1 = ['a','b','c','d']

def subproc(mylist):
    print()
    print('    subproc: mylist[]:', mylist)
    foo = mylist.pop()
    print('    subproc: mylist[]:', mylist)
    print()


if __name__ == '__main__':
#    print('main: list1[]:', list1)
#    print('main: run subproc(list1)')
#    subproc(list1)
#    print('main: list1[]:', list1)
#    print()

    datelst = ['Mon', 'Aug', '21', '06:00:00', 'EDT', '2020']
    datestr = 'Mon Aug 21 06:00:00 EDT 2020'

    print(datetime.strptime(datestr, '%a %b %d %H:%M:%S %Z %Y'))

# EOF:
