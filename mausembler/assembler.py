#!/bin/python

import sys,os

filename=sys.argv[1]

if os.path.exists(filename):
    fh=open(filename, 'rb')
    data=fh.readlines()
    fh.close()
else:
    print 'are you sure that file exists'