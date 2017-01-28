#!/usr/bin/python -OO
'''
remove extra headers from a group of CSV files

e.g. if you tell Spark to write to /tmp/output.csv, it will create a
_directory_ called /tmp/output.csv, and put in it (if successful) a bunch of
files part-00000-somethingsomething.csv, part-00001-somethingsomething.csv,
etc, and a _SUCCESS file. this filter expects all lines of all files in order
and removes every header _except for the very first one_.
'''
from __future__ import print_function
import sys, os

def process():
    sent_header = None
    for line in sys.stdin:
        if sent_header is None:
            header = line
            print(line, end='')  # still has its own EOL character(s)
            sent_header = True
        elif not line == header:
            try:
                print(line, end='')
            except IOError:  # broken pipe, most likely
                return  # ignore it

if __name__ == '__main__':
    process()
