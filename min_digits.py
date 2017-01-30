#!/usr/bin/python -OO
'''
remove unnecessary zeroes from floating-point numbers, and optionally
integers, in CSV files.

for comparing output with Pandas-generated CSV, which has sane rules for
floating point numbers, unlike Spark; and which trimmed the leading zeroes
from numeric strings used as keys in some input files.
'''
from __future__ import print_function
import sys, os, csv, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
sys.setcheckinterval(1000000000)

def process(ints=False, zeroes=False, strings=False, na=False):
    '''
    default is simply to cut down floating point digits to minimum.

    if ints==True, also trim leading zeroes from integers
    if zeroes==True, get rid of all floating zeroes, and if ints is true,
     the integer zeroes as well, replacing with null ('')
    if strings==True, map str.strip to all strings.
    if na==True, replace the string na to ''.
    '''
    filters = [trim_numbers]
    zerolist = ['0.0', '0.00']
    if zeroes:
        filters.insert(0, remove_zeroes)
        if ints:
            zerolist.extend(['0', '00', '000'])  # any more? 0000?
    else:
        zerolist[:2] = []  # get rid of floating point zeroes
    if na:
        zerolist.extend(['NA'])  # also na? Na? nA?
        if not remove_zeroes in filters:
            filters.append(remove_zeroes)
    if strings:  # trim everything before we convert to numbers
        filters.insert(0, trim_strings)
    reader = csv.reader(sys.stdin)
    writer = csv.writer(sys.stdout, lineterminator='\n')
    logging.debug('removing these zeroes: %s', zerolist)
    for row in reader:
        for munge in filters:
            row = munge(row, ints, zerolist)
        try:
            writer.writerow(row)
        except IOError:
            # assume pipeline was shut down
            break

def safe_number(string, ints):
    '''
    return a minimized numeric representation of string if it is one.
    '''
    try:
        integer = str(int(string))
        # leave leading zeroes unless user wants ints also minimized
        return integer if ints else string
    except ValueError:
        pass
    try:
        return str(float(string))
    except ValueError:
        return string

def trim_numbers(row, ints, *ignored):
    '''
    if value is floating point, return it minimized; no leading 
    or trailing zeroes.

    remember, float() will gladly cast an integer as a float. so
    we need to prevent that.
    '''
    return [safe_number(number, ints) for number in row]

def trim_strings(row, *ignored):
    '''
    strip leading and trailing spaces from all strings
    '''
    return map(str.strip, row)

def remove_zeroes(row, ignored, zerolist):
    return ['' if item in zerolist else item for item in row]

if __name__ == '__main__':
    # any non-null first arg passed enables integer processing as well as float
    # any non-null 2nd arg passed enables replacing zeroes with null ('').
    # any non-null 3rd arg passed enables trimming spaces from all strings.
    # any non-null 4th arg passed enables replacing NA with null ('').
    process(*map(bool, sys.argv[1:]))
