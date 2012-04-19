#!/bin/python

import sys
import os
import io
from custom_errors import *


class Assembler():
    def __init__(self, filename='null.txt', data=[]):
        self.ops = {'SET': 0x1, 'ADD': 0x2, 'SUB': 0x3, 'MUL': 0x4,
                  'DIV': 0x5, 'MOD': 0x6, 'SHL': 0x7, 'SHR': 0x8,
                  'AND': 0x9, 'BOR': 0xa, 'XOR': 0xb, 'IFE': 0xc,
                  'IFN': 0xd, 'IFG': 0xe, 'IVB': 0xf}  # 'DAT':0x}
        self.registers = {'A': 0x0, 'B': 0x1,
                          'C': 0x2, 'X': 0x3,
                          'Y': 0x4, 'Z': 0x5,
                          'I': 0x6, 'J': 0x7}
        self.input_filename = filename[1]
        self.output_filename = filename[2]
        print "Mausembler; self titled!\n"

    def load(self):
        if os.path.exists(self.input_filename):
            fh = open(self.input_filename, 'rb')
            data = fh.readlines()
            fh.close()
        else:
            print 'are you sure that file exists?'
        if os.path.exists(self.output_filename):
            cont = raw_input('Output file exists. Overwrite? ')
            if cont.lower() in ['yes', 'y']:
                self.output_file = io.open(self.output_filename, 'wb')
            else:
                print 'Exiting...'
                return 'OutFileExists'
        else:
            file = open(self.output_filename, 'w')
            file.write('')
            file.close()
            del file
            self.output_file = io.open(self.output_filename, 'wb')
        self.labels = {}
        print '\nThe cpu will be told to;'
        for self.line_number in range(len(data)):
            line = data[self.line_number]
            line = line.rstrip()
            line = line.replace(',', '')
            line = line.split()
            str(self.parse(line))
        self.output_file.close()
        print '\nLabels:', str(self.labels)

    def parse(self, opcode):
        if opcode != []:
            opcode[0] = opcode[0].upper()
            processed = 0
            if opcode[0][0] == ':':
                if opcode[0][1:] not in self.labels:
                    print '* remember line', str(self.line_number),
                    print 'as label', opcode[0][1:]
                    self.labels[opcode[0][1:]] = self.line_number
                else:
                    raise DuplicateLabelError(opcode[0][1:])
            if opcode[0] == 'SET':
                print '* set memory location', opcode[1], 'to', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            return processed
        else:
            print '* do nothing for this line'
