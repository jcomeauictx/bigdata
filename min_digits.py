#!/usr/bin/python -OO
'''
remove unnecessary zeroes from floating-point numbers, and optionally
integers, in CSV files.

for comparing output with Pandas-generated CSV, which has sane rules for
floating point numbers, unlike Spark; and which trimmed the leading zeroes
from numeric strings used as keys in some input files.
'''
from __future__ import print_function
import sys, os, csv

def process(ints_too=False, null_zeroes=False):
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    for row in reader:
        try:
            writer.writerow([trimdigits(column, ints_too, null_zeroes)
                             for column in row])
        except IOError:
            # assume pipeline was shut down
            break

def trimdigits(value, ints_too, null_zeroes):
    '''
    if value is floating point, or (optionally) integer, return it minimized;
    no leading or trailing zeroes.

    >>> trimdigits('0.0000', False, False)
    '0.0'
    >>> trimdigits('069', False, False)
    '069'
    >>> trimdigits('069', True, False)  # *not* octal, same as Pandas/Spark
    '69'
    >>> trimdigits('0x40', True, False)  # hex not supported
    '0x40'
    '''
    null = '' if null_zeroes else 0.0
    if value.isdigit():
        if ints_too:
            return str(int(value))
        else:
            pass  # `else` clause below keeps from returning it as float
    else:
        try:
            return str(float(value) or null)
        except ValueError:
            pass  # just return as a string
    return value

if __name__ == '__main__':
    # any first arg passed enables integer processing as well as float
    # any 2nd arg passed enables replacing floating point 0.0 with ''
    process(len(sys.argv) > 1, len(sys.argv) > 2)
