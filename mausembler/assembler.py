#!/bin/python

# This is a Quick & Dirty assembler :P


import os
import io
from mausembler.custom_errors import DuplicateLabelError
from mausembler.custom_errors import FileNonExistantError
from mausembler.custom_errors import FileExistsError


class Assembler():
    def __init__(self): #, data=[]):
        self.ops = {'SET': 0x1, 'ADD': 0x2, 'SUB': 0x3, 'MUL': 0x4,
                  'DIV': 0x5, 'MOD': 0x6, 'SHL': 0x7, 'SHR': 0x8,
                  'AND': 0x9, 'BOR': 0xa, 'XOR': 0xb, 'IFE': 0xc,
                  'IFN': 0xd, 'IFG': 0xe, 'IVB': 0xf}  # 'DAT':0x}
        self.registers = {'A': 0x0, 'B': 0x1,
                          'C': 0x2, 'X': 0x3,
                          'Y': 0x4, 'Z': 0x5,
                          'I': 0x6, 'J': 0x7}
        self.input_filename = ''
        self.output_filename = ''
        self.dependencies = []
        self.dep_path=[]
        self.labels = {}
        self.data=''
        print "Mausembler; self titled!\n"

    def determine_dependencies(self, data):
        for line in data:
            if line[0] == '.':
                if line.split()[0] == '.include':
                    self.dependencies.append(
                        ((''.join(line.split()[1:])).strip('"')).strip("'"))
        for dep in self.dependencies:
            self.load(dep, ''.join(dep.split('.')[:-1])+'bin')
#self.dep_path.append('\\'.join(input_filename.split('\\')[:-1]))
    def load(self, input_filename='null.txt', output_filename='null.bin'):
        self.dep_path.append('\\'.join(input_filename.split('\\')[:-1]))
        print 'self.dep_path:', str(self.dep_path)
        cur_input_filename = input_filename
        print 'manual:',os.getcwd()+input_filename
        if os.path.exists(os.getcwd()+'\\'+input_filename):
            input_filename = os.getcwd()+'\\'+input_filename
        while not os.path.exists(cur_input_filename):
            for x in range(len(self.dep_path)):
                print 'Poss'
                possibles=[(self.dep_path[x]+'\\'+cur_input_filename),
                           (self.dep_path[x]+'\\'+cur_input_filename.split('\\')[-1]),
                           (os.getcwd()+'\\'+self.dep_path[x]+'\\'+cur_input_filename),
                           (os.getcwd()+'\\'+self.dep_path[x]+'\\'+cur_input_filename.split('\\')[-1])]
                for poss in possibles:
                    print 'Poss:',poss
                    print os.path.exists(poss)
                    if os.path.exists(poss):
                        input_filename = poss
                        break
#                if os.path.exists(self.dep_path[x]+'\\'+cur_input_filename.split('\\')[-1]):
 #                   input_filename = self.dep_path[x]+'\\'+cur_input_filename
  #                  break
   #             if os.path.exists(os.getcwd()+'\\'+self.dep_path[x]+'\\'+cur_input_filename):
    #                input_filename = self.dep_path[x]+'\\'+cur_input_filename
     #               break
      #          if os.path.exists(os.getcwd()+'\\'+self.dep_path[x]+'\\'+cur_input_filename.split('\\')[-1]):
       #             input_filename = self.dep_path[x]+'\\'+cur_input_filename
        #            break
            print 'are you sure that file exists?\n\n'
            raise FileNonExistantError(input_filename)
        if os.path.exists(cur_input_filename):
            FH = open(input_filename, 'rb')
            self.data = FH.readlines()
            FH.close()
        if os.path.exists(output_filename):
            cont = raw_input('Output file exists. Overwrite? ')
            if cont.lower() in ['yes', 'y']:
                self.output_file = io.open(output_filename, 'wb')
            else:
                print 'Exiting...'
                raise FileExistsError(self.output_filename)
        else:
            FH = open(output_filename, 'w')
            FH.write('')
            FH.close()
            del FH
            self.output_file = io.open(output_filename, 'wb')
        self.determine_dependencies(self.data)
        print '\nThe cpu will be told to;'
        for self.line_number in range(len(self.data)):
            line = self.data[self.line_number]
            line = line.rstrip()
            line = line.replace(',', ' ')
            line = line.split()
            str(self.parse(line))
        self.output_file.close()
        print '\nDependencies:', str(self.dependencies)
        print 'Labels:', str(self.labels)

    def parse(self, opcode):
        if opcode != []:
            opcode[0] = opcode[0].upper()
            processed = 0
            if opcode[0][0] == ':':
                if opcode[0][1:] not in self.labels:
                    print '* remember line', str(self.line_number),
                    print 'as label "' + opcode[0][1:] + '"'
                    self.labels[opcode[0][1:]] = self.line_number
                else:
                    raise DuplicateLabelError(opcode[0][1:])
            if opcode[0] == 'SET':
                print '* set memory location', opcode[1], 'to', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            if opcode[0] == 'ADD':
                print '* set', opcode[1], 'to', opcode[1], '+', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            if opcode[0] == 'SUB':
                print '* set', opcode[1], 'to', opcode[1], '-', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            if opcode[0] == 'MUL':
                print '* set', opcode[1], 'to', opcode[1], '*', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            if opcode[0] == 'DIV':
                print '* set', opcode[1], 'to', opcode[1], '/', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            if opcode[0] == 'MOD':
                print '* set', opcode[1], 'to', opcode[1], '%', opcode[2]
                self.output_file.write(str(self.ops[opcode[0]]))
            return processed
        else:
            print '* do nothing for this line'
