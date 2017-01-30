#!/usr/bin/python -OO
'''
fix up normal PSV (pipe separated values) files and output as CSV.
'''
from __future__ import print_function
import sys, os, csv, logging
logging.basicConfig(level=logging.DEBUG if __debug__ else logging.INFO)
sys.setcheckinterval(1000000000)

def process():
    reader = csv.reader(sys.stdin, delimiter='|')
    writer = csv.writer(sys.stdout, lineterminator='\n')
    for row in reader:
        writer.writerow(row)

if __name__ == '__main__':
    process()
