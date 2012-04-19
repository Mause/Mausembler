#!/bin/python

import sys,os
from custom_errors import *

class Assembler():
    def __init__(self, filename='null.txt', data=[]):
        self.ops={'SET':0x1, 'ADD':0x2, 'SUB':0x3, 'MUL':0x4,
                  'DIV':0x5, 'MOD':0x6, 'SHL':0x7, 'SHR':0x8,
                  'AND':0x9, 'BOR':0xa, 'XOR':0xb, 'IFE':0xc,
                  'IFN':0xd, 'IFG':0xe, 'IVB':0xf}#'DAT':0x}
        self.registers={'A':0x0,'B':0x1,'C':0x2,'X':0x3,'Y':0x4,'Z':0x5,'I':0x6,'J':0x7}
        self.input_filename = filename[1]
        self.output_filename = filename[2]
        print "Mausembler; self titled!\n"
    def parse(self, opcode):
        if opcode != []:
            opcode[0]=opcode[0].upper()
            processed=0
            if opcode[0][0] == ':':
                if opcode[0][1:] not in self.labels:
                    self.labels[opcode[0][1:]] = self.line_number
                else:
                    raise DuplicateLabelError(opcode[0][1:])
            if opcode[0] == 'SET':
                print 'This is a set';
                print 'I will tell the cpu to;'
                print '     set memory location', opcode[1], 'to', opcode[2]
                processed = processed << self.ops[opcode[0]]
            return processed
    def load(self):
        if os.path.exists(self.input_filename):
            fh=open(self.input_filename, 'rb')
            data=fh.readlines()
            fh.close()
        else:
            print 'are you sure that file exists?'
        self.labels = {}
        for self.line_number in range(len(data)):
            line = data[self.line_number]
            print line,
            line = line.rstrip()
            line = line.strip(',')
            line = line.split()
            print 'Line:', line
            print 'Processed:', str(self.parse(line))+'\n'
        print self.labels