#!/usr/bin/python -OO
'''
remove duplicates with (simple) condition.
'''
from __future__ import print_function
import sys, os, csv, logging
from collections import OrderedDict, defaultdict
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

def process(all_or_all_but_one, any_value, *columns):
    r'''
    eliminate rows if there are duplicates on the given columns.

    first arg is either 'all' or 'all but one', indicating how many rows
    should be returned. be careful using 'all' because it means that the
    entire file must be buffered before any rows can be written. and
    we actually have to double-buffer it because the Unix pipe mechanism,
    which is how this is intended to be used, can give an "illegal seek"
    error. so we store the rowdicts in a buffer.

    next is the value which means "consider any value". the
    example below should make that clear. it removes rows where columns
    b and c have been output before and column c is 0.

    >>> from io import BytesIO
    >>> sys.stdin = BytesIO('a,b,c\n1,2,0\n2,3,0\n3,2,0\n4,2,1\n5,2,1')
    >>> process('all but one', '_any_', 'b', '_any_', 'c', '0')
    1,2,0
    2,3,0
    4,2,1
    5,2,1

    the next example shows that a prepended '!' to the column name reverses
    the check, and requires column c to *not* be '#'.
    >>> sys.stdin = BytesIO('a,b,c\n1,2,0\n2,2,#\n3,2,0\n4,2,#\n')
    >>> process('all but one', '_any_', 'b', '_any_', '!c', '#')
    1,2,0
    2,2,#
    4,2,#

    the final example shows an additional feature, that of prepending a '&'
    to show that the column should not be counted towards duplicates but
    should be a condition for printing.
    >>> sys.stdin = BytesIO('a,b,c\n1,2,0\n2,2,0\n3,2,1\n')
    >>> process('all', '_any_', 'b', '_any_', '&c', '0')
    3,2,1
    '''
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    header = reader.next()
    check, additional, seen = OrderedDict({}), OrderedDict({}), defaultdict(int)
    # sweet one-liner from http://stackoverflow.com/a/3125186/493161
    for k, v in map(None, *([iter(columns)] * 2)):
        if k.startswith('&'):
            if k[1:].startswith('!'):
                if v == any_value:
                    logging.warn('%s != (any value) will always return False',
                                 k[2:])
                additional[k[2:]] = ((lambda arg: False) if v == any_value else
                                     (lambda arg: arg != v))
                DOCTESTDEBUG('added additional check for column %s != %s',
                             k[2:], "(any value)" if v == any_value else v)
            else:
                additional[k[1:]] = ((lambda arg: True) if v == any_value else
                                     (lambda arg: arg == v))
                DOCTESTDEBUG('added additional check for column %s == %s',
                             k[1:], "(any value)" if v == any_value else v)
        elif k.startswith('!'):
            if v == any_value:
                logging.warn('%s != (any value) will always return False',
                             k[1:])
            check[k[1:]] = ((lambda arg: False) if v == any_value else
                            (lambda arg: arg != v))
            DOCTESTDEBUG('added duplicates check for %s == %s', k, v)
        else:
            check[k] = ((lambda arg: True) if v == any_value else
                        (lambda arg: arg == v))
            DOCTESTDEBUG('added duplicates check for %s == %s', k, v)
    DOCTESTDEBUG('check: %s, additional: %s', check, additional)

    def is_duplicate(rowdict, already_built=False):
        '''
        counts duplicate if all checks are True

        function has a side effect, building the duplicates list as it goes
        '''
        query = tuple([rowdict[c] for c in check])
        if not already_built:
            answer = seen[query]  # no need to `bool` it, 0 on first time seen
            seen[query] += all([check[c](rowdict[c]) for c in check])
            DOCTESTDEBUG('seen (unbuilt): %s, answer=%s', seen, answer)
        else:
            answer = seen[query] > 1
            DOCTESTDEBUG('seen (built): %s, answer=%s', seen, answer)
        return answer

    def is_match(rowdict):
        '''
        additional value checks beyond what counts as 'duplicate'
        '''
        DOCTESTDEBUG('looking for match of %s in %s',
                     [[c, rowdict[c]] for c in additional], additional)
        return all([additional[c](rowdict[c]) for c in additional])
    
    if all_or_all_but_one == 'all but one':
        DOCTESTDEBUG('testing the "all but one" loop')
        for row in reader:
            rowdict = OrderedDict(zip(header, row))
            if not (is_duplicate(rowdict) and is_match(rowdict)):
                writer.writerow(row)
    else:
        rowbuffer = []
        DOCTESTDEBUG('testing the "all" loop')
        DOCTESTDEBUG('first building the dictionary')
        for row in reader:
            rowbuffer.append(row)
            rowdict = OrderedDict(zip(header, row))
            is_duplicate(rowdict) # just populate the `seen` dictionary
        DOCTESTDEBUG('now performing the checks')
        for row in rowbuffer:
            rowdict = OrderedDict(zip(header, row))
            DOCTESTDEBUG('%s is_duplicate: %s, is_match: %s', row,
                         is_duplicate(rowdict, True),
                         is_match(rowdict))
            if not (is_duplicate(rowdict, True) and is_match(rowdict)):
                writer.writerow(row)

if __name__ == '__main__':
    process(*sys.argv[1:])
