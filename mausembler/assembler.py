#!/bin/python

import sys,os

class Assembler():
    def __init__(self, filename='null.txt', data=[]):
        self.ops={'SET':0x1, 'ADD':0x2, 'SUB':0x3, 'MUL':0x4,
                  'DIV':0x5, 'MOD':0x6, 'SHL':0x7, 'SHR':0x8,
                  'AND':0x9, 'BOR':0xa, 'XOR':0xb, 'IFE':0xc,
                  'IFN':0xd, 'IFG':0xe, 'IVB':0xf}#'DAT':0x}
        self.registers={'A':0x0,'B':0x1,'C':0x2,'X':0x3,'Y':0x4,'Z':0x5,'I':0x6,'J':0x7}
        self.input_filename = filename[1]
        self.output_filename = filename[2]
        print "Quick&Dirty, remember that"
    def parse(self, opcode):
        opcode[0]=opcode[0].upper()
        processed=''
        print 'Okay, this looks like a', opcode[0]
        if opcode[0] == 'SET': print 'This is a set';(str(processed)+str(self.ops[opcode[0]]))
        print 'Processed:',processed+'\n'
        return processed
    def load(self):
        if os.path.exists(self.input_filename):
            fh=open(self.input_filename, 'rb')
            data=fh.readlines()
            fh.close()
        else:
            print 'are you sure that file exists?'

        for line in data:
            print line
            print 'Proccessed:', self.parse(line.split())


