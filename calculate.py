#!/usr/bin/python -OO
'''
calculate new column from other, existing, columns

assumes "add" unless column name begins with '-'. NOTE that some columns
are named with leading asterisks, so we cannot use that for multiplication
with this scheme.
'''
from __future__ import print_function
import sys, os, csv, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
sys.setcheckinterval(1000000000)

def process(columns):
    result_name = columns.pop(0)
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    additions, subtractions = [], []
    try:
        header = reader.next()
        if result_name in header:
            result_index = header.index(result_name)
        else:
            header.append(result_name)
            result_index = -1
        writer.writerow(header)
        for columnname in columns:
            if columnname.startswith('-'):
                try:
                    subtractions.append(header.index(columnname[1:]))
                except ValueError:
                    raise(IndexError('key %s not found in columns %s' % (
                        columnname[1:], header)))
            else:
                try:
                    additions.append(header.index(columnname))
                except ValueError:
                    raise(IndexError('key %s not found in columns %s' % (
                        columnname, header)))
    except IOError:
        logging.debug('apparently pipeline was shut down')
        sys.exit(1)
    for row in reader:
        if result_index == -1:
            row.append(0.0)
        for index in additions:
            try:
                row[result_index] += float(row[index] or '0')
            except (TypeError, ValueError):
                raise(ValueError('could not add %s with %s' % (
                    row[index], row[-1])))
        for index in subtractions:
            try:
                row[result_index] -= float(row[index] or '0')
            except (TypeError, ValueError):
                raise(ValueError('could not add %s with %s' % (
                    row[index], row[-1])))
        writer.writerow(row)

if __name__ == '__main__':
    process(sys.argv[1:])
