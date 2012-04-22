#!/bin/python
# This is a Quick & Dirty assembler :P
"This is a Quick & Dirty assembler :P"
import os
#import io
import binascii
from mausembler.custom_errors import DuplicateLabelError
from mausembler.custom_errors import FileNonExistantError
from mausembler.custom_errors import FileExistsError
from mausembler.sparser import Sparser


class Assembler():
    "Does the assembling stuff :D"
    def __init__(self):
        self.ops = {'SET': 0x1, 'ADD': 0x2, 'SUB': 0x3, 'MUL': 0x4,
                  'DIV': 0x5, 'MOD': 0x6, 'SHL': 0x7, 'SHR': 0x8,
                  'AND': 0x9, 'BOR': 0xa, 'XOR': 0xb, 'IFE': 0xc,
                  'IFN': 0xd, 'IFG': 0xe, 'IVB': 0xf}  # 'DAT':0x}
        self.registers = {'A': 0x00, 'B': 0x01,
                          'C': 0x02, 'X': 0x03,
                          'Y': 0x04, 'Z': 0x05,
                          'I': 0x06, 'J': 0x07,
                          '[A]': 0x08, '[B]': 0x09,
                          '[C]': 0x0a, '[X]': 0x0b,
                          '[Y]': 0x0c, '[Z]': 0x0d,
                          '[I]': 0x0e, '[J]': 0x0f,
                          # Special registers
                          # 0x10-0x17: [next word + register] goes here
                          'POP': 0x18, '[SP++]': 0x18,
                          'PEEK': 0x19, '[SP]': 0x19,
                          'PUSH': 0x1a, '[--SP]': 0x1a,
                          'SP': 0x1b, 'PC': 0x1c,
                          'O': 0x1d, '[PC++]': 0x1e,
                          'PC++': 0x1f}
        self.input_filename = ''
        self.input_file = None
        self.output_file = None
        self.output_filename = ''
        self.dependencies = []
        self.dep_path = []
        self.labels = {}
        self.data_done = []
        self.data = ''
        self.sparser = Sparser()
        self.tobe_written_data = []
        self.conditioned_data = []
        self.line_number = 0

        print "Mausembler; self-titled!\n"

    def determine_dependencies(self, data):
        """Simply loops through each line in the file,
        and determines which files the file depends on"""
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
        """Does in depth checking for input file,
        loads said input file, prepares output file, etc"""
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
            for X in range(len(self.dep_path)):
                possibles = [(self.dep_path[X] + '\\' + cur_input_filename),
                             (self.dep_path[X] + '\\' + \
                              cur_input_filename.split('\\')[-1]),
                             (os.getcwd() + '\\' + self.dep_path[X] + '\\' + \
                              cur_input_filename),
                             (os.getcwd() + '\\' + self.dep_path[X] + '\\' + \
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
                self.output_file = open(output_filename, 'wb')
            else:
                print 'Exiting...'
                raise FileExistsError(self.output_filename)
        else:
            FH = open(output_filename, 'w')
            FH.write('')
            FH.close()
            del FH
            self.output_file = open(output_filename, 'wb')
        self.determine_dependencies(self.data)
        print "\nFinding labels..."

        # these next couple of lines will conditions the data to
        # prepare it for parsing
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
        for opcode in self.conditioned_data:
            self.find_labels(opcode)
        print '\nFor', self.input_filename, 'the cpu will be told to;'

        # this is the second loop; it'll do the actual assembling
        for opcode in self.conditioned_data:
            str(self.parse(opcode, input_filename))
        print '\nDependencies:', str(self.dependencies)
        print 'Labels:', [label for label in self.labels]
        print '\n'
        print "I'm just about to write all this shit to file :)\n\n"
        for line in self.tobe_written_data:
            print 'line:', line
            if line != '' and line != ():
                self.output_file.write(binascii.a2b_hex(line))
        self.output_file.close()

        #self.output_file.close()

    def find_labels(self, opcode):
        if opcode != []:
            opcode[0] = opcode[0].upper()
            processed = 0
            if opcode[0][0] == ':':
                label_name = opcode[0][1:]
                if label_name not in self.labels:
                    print '* remember line', str(self.line_number),
                    print 'as label "' + label_name + '"'
                    if label_name in self.labels:
                        raise DuplicateLabelError([label_name,
                                                   self.input_filename,
                                                   self.labels,
                                                   self.line_number])
                    self.labels[label_name.upper()] = self.line_number
            elif opcode[0][-1] == ':':
                label_name = opcode[0][:-1]
                if label_name not in self.labels:
                    print '* remember line', str(self.line_number),
                    print 'as label "' + label_name + '"'
                    if label_name in self.labels:
                        raise DuplicateLabelError([label_name,
                                                   self.input_filename,
                                                   self.labels,
                                                   self.line_number])
                    self.labels[label_name.upper()] = self.line_number
        else:
            print '* doing nothing for this line'

    def parse(self, opcode, input_filename):
        "Does minimal processing, calls the parser"
        if opcode != []:
            opcode[0] = opcode[0].upper()
            self.tobe_written_data.append(self.sparser.parse(self, opcode))
        else:
            print '* do nothing for this line'
