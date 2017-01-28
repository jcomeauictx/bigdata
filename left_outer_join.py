#!/usr/bin/python -OO
'''
implement a left outer join of two CSV tables on the same-named column in each.

this functions as a filter. pass in the column name and the right table
filename as args, while the left table comes through the pipeline as sys.stdin.
this way you can pipeline any number of joins.

if the right table needs preprocessing, as many of mine will, use
SHELL=/bin/bash in the Makefile, and use process substitution to filter
them, e.g.:
    cat intermediate.csv | ./left_outer_join.py 'Customer ID - Key' \
        <(cat bad.psv | tr '\222' "'" | ./bad_psv.py)
'''
from __future__ import print_function
import sys, os, csv, logging
from collections import defaultdict
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

COMMAND = os.path.splitext(os.path.basename(sys.argv[0]))[0]
DOCTESTDEBUG = logging.debug if COMMAND == 'doctest' else lambda *args: None

def process(key, right_hand_table):
    '''
    read lines as CSV and perform a left outer join, which means, in
    my particular context (pseudocode):

    foreach left_row in left_hand_table:
     foreach right_row in right_hand_table:
      if right_row[key] == left_row[key]:
       left_hand_table.insert(left_row + filter_out(key, right_row))
    
    don't trap reader.next() on first lines; we want to know
    if it breaks there. past that point, we can simply assume someone ran
    `head` or `tail` or something similar to truncate the data.
    '''
    right_header, right_index, right_data = build_dict(right_hand_table, key)
    left_reader = csv.reader(sys.stdin)
    left_header = left_reader.next()
    if not key in left_header:
        raise ValueError('Specified key "%s" not found in'
                         ' left hand table headers %s' % (key, left_header))
    left_index = left_header.index(key)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    writer.writerow(left_header + right_header)
    no_match = [''] * len(right_header)
    for row in left_reader:
        lastcolumns = right_data.get(row[left_index], [no_match])
        for columns in lastcolumns:
            writer.writerow(row + columns)

def build_dict(filename, key):
    r'''
    build a dict, keyed with the given key, of data in the right-hand table.

    ugly hack put in to use an open file object for testing.

    >>> from io import BytesIO
    >>> build_dict(BytesIO('a,b,c\n1,2,3\n4,5,6\n'), 'b')
    (['a', 'c'], 1, {'2': [['1', '3']], '5': [['4', '6']]})
    '''
    data = defaultdict(list)
    if isinstance(filename, basestring):
        infile = open(filename)
    else:
        infile = filename
    with infile as tableinput:
        reader = csv.reader(tableinput)
        header = reader.next()
        DOCTESTDEBUG('header: %s', header)
        if not key in header:
            raise ValueError('Specified key "%s" not found in'
                             ' right hand table headers %s' % (
                             key, header))
        index = header.index(key)
        DOCTESTDEBUG('index of key %s: %d', key, index)
        right_header = [h for h in header if h != key]
        DOCTESTDEBUG('right header: %s', right_header)
        for row in reader:
            trimmed = [row[i] for i in range(len(row)) if i != index]
            DOCTESTDEBUG('row: %s, trimmed: %s', row, trimmed)
            rowkey = row[index]
            DOCTESTDEBUG('rowkey: %s', rowkey)
            if rowkey in data:
                if not trimmed in data[rowkey]:
                    data[rowkey].append(trimmed)
                else:
                    logging.warn('Discarding duplicate row'
                                 ' in right-hand table: %s',
                                 trimmed)
            else:
                data[rowkey].append(trimmed)
    logging.debug('data table for %s successfully built', filename)
    return right_header, index, dict(data)

if __name__ == '__main__':
    process(*sys.argv[1:])
