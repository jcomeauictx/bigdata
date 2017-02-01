#!/usr/bin/python -OO
'''
remove duplicates with (simple) condition.
'''
from __future__ import print_function
import sys, os, csv, logging
from collections import OrderedDict
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
sys.setcheckinterval(1000000000)
# http://stackoverflow.com/a/41856587/493161
COMMAND = os.path.splitext(os.path.basename(sys.argv[0]))[0]
if COMMAND in ['doctest', 'pydoc']:
    NONDOCTESTPRINT = lambda *args, **kwargs: None
    DOCTESTDEBUG = logging.debug
else:
    NONDOCTESTPRINT = print
    DOCTESTDEBUG = lambda *args, **kwargs: None

def process(columns):
    r'''
    eliminate rows if there are duplicates on the given columns.

    first `column` is the value which means "consider any value". the
    example below should make that clear. it removes rows where columns
    b and c have been output before and column c is 0.

    >>> from io import BytesIO
    >>> sys.stdin = BytesIO('a,b,c\n1,2,0\n2,3,0\n3,2,0\n4,2,0\n5,2,1\n')
    >>> process(['_all_', 'b', '_all_', 'c', '0'])
    1,2,0
    2,3,0
    5,2,1
    '''
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    header = reader.next()
    all_marker = columns.pop(0)
    # sweet one-liner from http://stackoverflow.com/a/3125186/493161
    check = OrderedDict([k,
        (lambda arg: True) if v == all_marker else
        (lambda arg: arg == v)] for k, v in map(None, *([iter(columns)] * 2)))
    DOCTESTDEBUG('check: %s', check)
    additional = dict([[k[1:], check.pop(k)] for k in list(check)
                      if k.startswith('&')])
    seen = {}

    def is_duplicate(rowdict):
        '''
        inner function has a side effect, building the duplicates list as it
        goes.
        '''
        query = tuple([rowdict[c] for c in check])
        checked = [check[c](rowdict[c]) for c in check]
        answer = query in seen
        if all(checked):
            seen[query] = checked
        DOCTESTDEBUG('seen: %s, answer=%s', seen, answer)
        return answer

    def is_match(rowdict):
        '''
        additional value checks beyond what counts as 'duplicate'
        '''
        return all([additional[c](rowdict[c]) for c in additional])

    for row in reader:
        rowdict = OrderedDict(zip(header, row))
        if not (is_duplicate(rowdict) and is_match(rowdict)):
            writer.writerow(row)

if __name__ == '__main__':
    process(sys.argv[1:])
