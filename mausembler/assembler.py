#!/bin/python
# This is a Quick & Dirty assembler :P

import os
import io
import binascii
from mausembler.custom_errors import DuplicateLabelError
from mausembler.custom_errors import FileNonExistantError
from mausembler.custom_errors import FileExistsError
from mausembler.sparser import Sparser


class Assembler():
    def __init__(self):
        self.ops = {'SET': 0x1, 'ADD': 0x2, 'SUB': 0x3, 'MUL': 0x4,
                  'DIV': 0x5, 'MOD': 0x6, 'SHL': 0x7, 'SHR': 0x8,
                  'AND': 0x9, 'BOR': 0xa, 'XOR': 0xb, 'IFE': 0xc,
                  'IFN': 0xd, 'IFG': 0xe, 'IVB': 0xf}  # 'DAT':0x}
        self.registers = {'A': 0x0, 'B': 0x1,
                          'C': 0x2, 'X': 0x3,
                          'Y': 0x4, 'Z': 0x5,
                          'I': 0x6, 'J': 0x7,
                          # Special registers
                          'PC': 0x1c, 'POP': 0x18}
        self.input_filename = ''
        self.output_filename = ''
        self.dependencies = []
        self.dep_path = []
        self.labels = {}
        self.data_done = []
        self.data = ''
        self.sparser = Sparser()
        self.tobe_written_data = []
        print "Mausembler; self-titled!\n"

    def determine_dependencies(self, data):
        print "Determining dependencies..."
        if data not in self.data_done:
            self.data_done.append(data)
        else:
            return
        for line in data:
            if line[0] == '.':
                if line.split()[0] == '.include':
                    self.dependencies.append(
                        ((''.join(line.split()[1:])).strip('"')).strip("'"))
        for dep in self.dependencies:
            self.load(dep, ''.join(dep.split('.')[:-1]) + 'bin')
#self.dep_path.append('\\'.join(input_filename.split('\\')[:-1]))

    def load(self, input_filename='null.txt', output_filename='null.bin'):
        print 'Input file:', str(input_filename)
        print 'Output file:', str(output_filename)
        print
        #self.dep_path.append('\\'.join(input_filename.split('\\')[:-1]))
        abspath = os.path.abspath(input_filename)
        self.dep_path.append('\\'.join(abspath.split('\\')[:-1]))
        del abspath
        print 'self.dep_path:', str(self.dep_path)
        cur_input_filename = input_filename

        if os.path.exists(os.getcwd() + '\\' + input_filename):
            input_filename = os.getcwd() + '\\' + input_filename
        while not os.path.exists(input_filename):
            for x in range(len(self.dep_path)):
                possibles = [(self.dep_path[x] + '\\' + cur_input_filename),
                             (self.dep_path[x] + '\\' + \
                              cur_input_filename.split('\\')[-1]),
                             (os.getcwd() + '\\' + self.dep_path[x] + '\\' + \
                              cur_input_filename),
                             (os.getcwd() + '\\' + self.dep_path[x] + '\\' + \
                              cur_input_filename.split('\\')[-1])]
                for poss in possibles:
#                    print os.path.exists(poss)
                    if os.path.exists(poss):
                        input_filename = poss
                        break
            if not os.path.exists(input_filename):
                print 'are you sure that the specified file exists?\n\n'
                raise FileNonExistantError(input_filename)
        print
        if os.path.exists(cur_input_filename):
            FH = open(input_filename, 'rb')
            self.data = FH.readlines()
            FH.close()
        if os.path.exists(output_filename):
            #cont = raw_input('Output file exists. Overwrite? ')
            # ^ commenting this line out while testing
            cont = 'yes'
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
        print "\nFinding labels..."

        # these next couple of lines will conditions the data to
        # prepare it for parsing
        self.conditioned_data = []
        for self.line_number in range(len(self.data)):
            opcode = self.data[self.line_number]
            opcode = opcode.rstrip()
            opcode = opcode.replace(',', ' ')
            # for now the tokeniser assumes that there
            # are no strings that contain semicolons
            opcode = opcode.split(';')[0]
            opcode = opcode.split()
            self.conditioned_data.append(opcode)

        # this is the first loop; it'll find stuff like labels and shit
#        for self.line_number in range(len(self.data)):
 #           opcode = self.data[self.line_number]
  #          opcode = opcode.rstrip()
   #         opcode = opcode.replace(',', ' ')
    #        # for now the tokeniser assumes that there
     #       # are no strings that contain semicolons
      #      opcode = opcode.split(';')[0]
       #     opcode = opcode.split()
        for opcode in self.conditioned_data:
            self.find_labels(opcode)
        print '\nThe cpu will be told to;'
        # this is the second loop; it'll do the actual assembling
#        for self.line_number in range(len(self.data)):
 #           opcode = self.data[self.line_number]
  #          opcode = opcode.rstrip()
   #         opcode = opcode.replace(',', ' ')
    #        # for now the tokeniser assumes that there are no strings that contain semicolons
     #       opcode = opcode.split(';')[0]
      #      opcode = opcode.split()
        for opcode in self.conditioned_data:
            str(self.parse(opcode, input_filename))
        print '\nDependencies:', str(self.dependencies)
        print 'Labels:', [label for label in self.labels]
        print '\n'
        print self.tobe_written_data
        print '\n\n'
        print "I'm just about to write all this shit to file :)\n\n"
        for line in self.tobe_written_data:
            print line
            if line != '':
                bytes = binascii.a2b_hex(line)
                self.output_file.write(bytes)
        self.output_file.close()

        #self.output_file.close()

    def find_labels(self, opcode):
        if opcode != []:
            opcode[0] = opcode[0].upper()
            processed = 0
            if opcode[0][0] == ':':
                label_name = opcode[0][1:]
                if label_name not in self.labels:
                    print '* remember line', str(self.line_number), 'as label "' + label_name + '"'
                    self.labels[label_name] = self.line_number
                    if self.line_number != self.labels[label_name]:
                        raise DuplicateLabelError([label_name, input_filename,
                                                   self.labels, self.line_number])
            elif opcode[0][-1] == ':':
                label_name = opcode[0][:-1]
                if label_name not in self.labels:
                    print '* remember line', str(self.line_number), 'as label "' + label_name + '"'
                    self.labels[label_name] = self.line_number
                    if self.line_number != self.labels[label_name]:
                        raise DuplicateLabelError([label_name, input_filename,
                                                   self.labels, self.line_number])
        else:
            print '* doing nothing for this line'

    def parse(self, opcode, input_filename):
        if opcode != []:
            opcode[0] = opcode[0].upper()
            self.tobe_written_data.append( self.sparser.parse(self, opcode) )
        else:
            print '* do nothing for this line'
