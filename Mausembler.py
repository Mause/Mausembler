#!/bin/python3
import os
import sys
from pprint import pprint

from mausembler import Assembler

input_filename = os.path.abspath(sys.argv[1])
output_filename = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else 'null.bin')

with open(input_filename) as file_handle:
    assembly = file_handle.readlines()


test = Assembler({'input_directory': os.path.abspath(os.path.dirname(input_filename))})
assembly = test.assemble(assembly)

pprint(assembly)
