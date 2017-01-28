#!/usr/bin/python -OO
'''
fixup CSV files written by Spark whose columns were reordered during join

this functions as a filter.
the first row fed to it is the reference row. it must include all columns,
in the expected order, that can appear in the remaining output (from the
Spark-written files). the following lines will either be headers or data
rows; it will reorder them all, and send them to the header remover that
is the next program in the pipeline.
'''
from __future__ import print_function
import sys, os, csv, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

def process():
    '''
    read lines as CSV and send them through reordering routine
    
    don't trap reader.next() on first two lines; we want to know
    if it breaks there. past that point, we can simply assume someone ran
    `head` or `tail` or something similar to truncate the data.

    we can also assume that the reference columns will be the same length,
    or shorter, than the disordered columns, since the disordering is
    expected to have resulted from a Spark df.join().
    '''
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    row = reader.next()
    logging.debug('setting reference to %s', row)
    reference = row
    row = reader.next()
    logging.debug('setting disordered to %s', row)
    disordered = row
    try:
        reindex = [disordered.index(column) for column in reference]
    except ValueError as failed:  # item not in list, probably not a CSV header
        logging.error("Problem: doesn't look like a CSV header: %s", disordered)
        raise failed
    # now remove needless indices, those that are equal to their
    # position in the list
    while reindex and reindex[-1] == len(reindex) - 1:
        reindex.pop(-1)
    writer.writerow(reference + disordered[len(reference):])
    for row in reader:
        try:
            writer.writerow(reorder(row, reindex))
        except IOError:  # broken pipe from `head` likely
            break  # ignore it

def reorder(row, order):
    '''
    >>> reorder(['b', 'a', 'c', 'd', 'e'], [1, 0, 2])
    ['a', 'b', 'c', 'd', 'e']
    >>> reorder(['this', 'should', 'just', 'pass', 'through'], [])
    ['this', 'should', 'just', 'pass', 'through']
    '''
    row[:len(order)] = [row[n] for n in order]
    return row

if __name__ == '__main__':
    process()
