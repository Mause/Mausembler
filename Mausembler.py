#!/bin/python
import sys
from mausembler import Assembler


test = Assembler()
test.load(sys.argv[1], sys.argv[2])
