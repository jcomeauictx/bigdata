#!/usr/bin/python -OO
'''
remove duplicates with condition.
'''
from __future__ import print_function
import sys, os, csv, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
sys.setcheckinterval(1000000000)

def process(columns):
    r'''
    eliminate rows if there are duplicates on the given columns.

    first `column` is the value which means "consider any value". the
    example below should make that clear. it removes rows where columns
    b and c have been output before and column c is 0.

    >>> from io import BytesIO
    >>> sys.stdin = BytesIO('a,b,c\n,1,2,0\n2,3,0\n3,2,0\n4,2,0\n,5,2,1\n')
    >>> process(['_all_', 'b', '_all_', 'c', '0'])
    '''
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    header = reader.next()
    all_marker = columns.pop(0)
    # sweet one-liner from http://stackoverflow.com/a/3125186/493161
    conditions = dict(map(None, *([iter(columns)] * 2)))
    duplicates = []
    def is_duplicate(row):
        '''
        inner function has side effects, building the duplicates list as it
        goes.
        '''
        rowdict = dict(zip(header, row))
        columns = [rowdict[c] if conditions[c] != all_marker else all_marker
                   for c in conditions]
        answer = True if columns in duplicates else False
        duplicates.append(columns)
        return answer
    for row in reader:
        if not is_duplicate(row):
            writer.writerow(row)

if __name__ == '__main__':
    process(sys.argv[1:])
