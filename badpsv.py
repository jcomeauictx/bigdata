#!/usr/bin/python -OO
'''
fix up bad PSV (pipe separated values) files and output as CSV.

these particular "bad" files were made "manually", and have an extra set of
quotes around each row, which doubles the interior quotes, as though the
creator took an original PSV file and repackaged it as CSV; since there are
no commas, the entire line was taken as a column.

also, one row of one table was a column short. although the missing column
was most likely 2nd from the left, can't count on that. so just append one.
not dealing with extra columns for now, since there don't seem to be any.

NOTE: this must only be used on short files, as it buffers the entire
file in RAM!
'''
from __future__ import print_function
import sys, os, csv, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)

def process():
    reader = csv.reader(sys.stdin, delimiter='|')
    writer = csv.writer(sys.stdout, lineterminator='\n')
    firstpass = [r for r in reader]
    logging.debug('first pass: %s', firstpass[:2])
    if len(firstpass[0]) > 1:
        # assume it was not a "bad" file after all.
        writer.writerows(firstpass)
        return
    # presumed bad, so now read the normal CSV record
    finalpass = [csv.reader(r, delimiter='|').next() for r in firstpass]
    logging.debug('final pass: %s', finalpass[:2])
    logging.debug('correcting any short rows...')
    header = finalpass[0]
    for row in finalpass:
        # I know this is horribly inefficient but it's only meant to
        # deal with *one* column in *one* row of *one* table
        while len(row) < len(header):
            row += ['']
        writer.writerow(row)
    logging.debug('done corrections')

if __name__ == '__main__':
    process()
