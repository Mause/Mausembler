#!/bin/python
# This is a Quick & Dirty assembler :P
"This is a Quick & Dirty assembler :P"
import os
import sys
import binascii
import logging
try:
    from mausembler.custom_errors import DuplicateLabelError
    from mausembler.custom_errors import FileNonExistantError
    from mausembler.custom_errors import FileExistsError
except ImportError:
    from custom_errors import DuplicateLabelError
    from custom_errors import FileNonExistantError
    from custom_errors import FileExistsError


class Assembler():
    "Does the assembling stuff :D"
    def __init__(self):
        self.ops = {'SET': 0x01, 'ADD': 0x02, 'SUB': 0x03,
                    'MUL': 0x04, 'MLI': 0x05, 'DIV': 0x06,
                    'DVI': 0x07, 'MOD': 0x08, 'AND': 0x09,
                    'BOR': 0x0a, 'XOR': 0x0b, 'SHR': 0x0c,
                    'ASR': 0x0d, 'SHL': 0x0e, 'IFB': 0x10,
                    'IFC': 0x11, 'IFE': 0x12, 'IFN': 0x13,
                    'IFG': 0x14, 'IFA': 0x15, 'IFL': 0x16,
                    'IFU': 0x17}  # 'DAT':0x}
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
        self.tobe_written_data = []
        self.conditioned_data = []
        self.line_number = 0
        self.log_file = ''
        # set the instance.debug_toggle
        # switch for debug info
        self.debug_toggle = False
        print "Mausembler; self-titled!\n"

    def debug(self, data):
        "Simply debug function"
        if data[0] == 'p':
            data = '* ' + data[1:]
        elif data[0] == 's':
            data = '    * ' + data[1:]
        self.log_file.info(data)
        if self.debug_toggle == True:
            print data

    def load(self, input_filename='null.txt', output_filename='null.bin'):
        """Does in depth checking for input file,
        loads said input file, prepares output file,
        sets up log file"""

        # first off, (very important)
        # we have to setup a log file!
        self.log_file = logging.getLogger('Mausembler')
        hdlr = logging.FileHandler('Mausembler.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.log_file.addHandler(hdlr)
        self.log_file.setLevel(logging.INFO)
        self.log_file.info('##########################################')
        self.log_file.info('Mausembler! Self-titled!')
        self.log_file.info('##########################################')

        print 'Input file:', str(input_filename)
        self.log_file.info('Input file: ' + str(input_filename))
        self.input_filename = input_filename
        print 'Output file:', str(output_filename)
        self.log_file.info('Output file: ' + str(output_filename))
        self.output_filename = output_filename
        #self.dep_path.append('\\'.join(input_filename.split('\\')[:-1]))
        abspath = os.path.abspath(input_filename)
        self.dep_path.append('\\'.join(abspath.split('\\')[:-1]))
        del abspath
        self.debug('pself.dep_path: ' + str(self.dep_path))
        cur_input_filename = input_filename

        if os.path.exists(os.getcwd() + '\\' + input_filename):
            input_filename = os.getcwd() + '\\' + input_filename

        for num in range(len(self.dep_path)):
            possibles = [(self.dep_path[num] + '\\' + cur_input_filename),
                         (self.dep_path[num] + '\\' + \
                          cur_input_filename.split('\\')[-1]),
                         (os.getcwd() + '\\' + self.dep_path[num]\
                          + '\\' + cur_input_filename),
                         (os.getcwd() + '\\' + self.dep_path[num]\
                          + '\\' + cur_input_filename.split('\\')[-1])]
            for poss in possibles:
                self.debug('s' + poss + ' ' + str(os.path.exists(poss)))
                if os.path.exists(poss):
                    input_filename = poss
                    break
        if not os.path.exists(input_filename):
            print 'are you sure that the specified file exists?\n\n'
            self.log_file.info('are you sure that the specified file exists?')
            raise FileNonExistantError(input_filename)
        print
        if os.path.exists(cur_input_filename):
            file_handle = open(input_filename, 'rb')
            self.data = file_handle.readlines()
            file_handle.close()
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
            file_handle = open(output_filename, 'w')
            file_handle.write('')
            file_handle.close()
            del file_handle
            self.output_file = open(output_filename, 'wb')
        self.do_dependencies(self.data)
        self.debug("pFinding labels...")

        # these next couple of lines will condition the data to
        # prepare it for parsing
        for self.line_number in range(len(self.data)):
            opcode = self.data[self.line_number]
            opcode = opcode.rstrip()
            opcode = opcode.replace(',', ' ')
            # for now the tokeniser assumes that there
            # are no strings that contain semicolons
            # looking at regex to correct this
            # but i dont think even that will be fool
            # proof
            opcode = opcode.split(';')[0]
            opcode = opcode.split()
            self.conditioned_data.append(opcode)

        # this is the first loop; it'll find stuff like labels and shit
        for opcode in self.conditioned_data:
            self.find_labels(opcode)
        if self.input_filename == '':
            self.debug('pOkay. \
            The input_filename variable is empty. NOT HELPFUL')
            self.debug('pthe cpu will be told to')
        else:
            self.debug('pfor "' + self.input_filename\
                       + '" the cpu will be told to;')

        # this is the second loop; it'll do the actual assembling
        for opcode in self.conditioned_data:
            str(self.go_parse(opcode))
        if len(self.dependencies) != 0:
            self.debug('pDependencies: ' + str(self.dependencies))
        else:
            self.debug('pThe input file was not found \
to depend on any external code bases')
        if len(self.labels) != 0:
            self.debug('pLabels: ' + str([label for label in self.labels]))
        else:
            self.debug('pNo labels were found in the input file')
        self.debug('pAbout to write output data to "' + output_filename + '"')
        errors = 0
        total_lines = 0
        for line in self.tobe_written_data:
            if line != '' and line != () and line != []:
                self.debug('pline: ' + line)
                total_lines += 1
                try:
                    self.output_file.write(binascii.a2b_hex(line))
                except TypeError:
                    print 'Odd-length string:', str(line)
                    self.log_file.info('Odd-length string: ' + str(line))
                    errors += 1
        self.output_file.close()
        if errors != 0:
            print
            print str(errors), 'out of', str(total_lines),\
                  'parseable lines threw errors'
            self.log_file.info(str(errors) + ' out of '\
                               + str(total_lines) +\
                               ' parseable lines threw errors')
        print '\nDone\n'
        self.log_file.info('Done')

        #self.output_file.close()

    def do_dependencies(self, data):
        """Simply loops through each line in the file,
        and determines which files the file depends on"""
        self.debug("pDetermining dependencies...")
        if data not in self.data_done:
            self.data_done.append(data)
        else:
            return
        for line in data:
            if line[0] == '.':
                if line.split()[0] == '.include':
                    self.dependencies.append(
                        ((''.join(line.split()[1:])).strip('"')).strip("'"))

        self.debug('pdeps ' + str(self.dep_path))

        for dep in self.dependencies:
            for num in range(len(self.dep_path)):
                possibles = [(self.dep_path[num] + '\\' + dep),
                             (self.dep_path[num] + '\\' + \
                              dep.split('\\')[-1]),
                             (os.getcwd() + '\\' + self.dep_path[num]\
                              + '\\' + dep),
                             (os.getcwd() + '\\' + self.dep_path[num]\
                              + '\\' + dep.split('\\')[-1])]
                for poss in possibles:
                    self.debug('p' + poss + ' ' + str(os.path.exists(poss)))
                    if os.path.exists(poss):
                        dep = poss
                        break
            dep_handler = open(dep, 'rb')
            for line in dep_handler.readlines():
                self.data.append(line)
            dep_handler.close()

# old reference code :P
#self.dep_path.append('\\'.join(input_filename.split('\\')[:-1]))

    def find_labels(self, opcode):
        "Find labels in the input file"
        if opcode != []:
            opcode[0] = opcode[0].upper()
            if opcode[0][0] == ':':
                label_name = opcode[0][1:]
                if label_name not in self.labels:
                    self.debug('premember line ' + str(self.line_number) +\
                               ' as label "' + label_name + '"')
                    if label_name in self.labels:
                        raise DuplicateLabelError([label_name,
                                                   self.input_filename,
                                                   self.labels,
                                                   self.line_number])
                    self.labels[label_name.upper()] = self.line_number
            elif opcode[0][-1] == ':':
                label_name = opcode[0][:-1]
                if label_name not in self.labels:
                    self.debug('premember line ' + str(self.line_number)\
                               + ' as label "' + label_name + '"')
                    if label_name in self.labels:
                        raise DuplicateLabelError([label_name,
                                                   self.input_filename,
                                                   self.labels,
                                                   self.line_number])
                    self.labels[label_name.upper()] = self.line_number
        else:
            self.debug('pdoing nothing for this line')

    def go_parse(self, opcode):
        "Does minimal processing, calls the parser"
        if opcode != []:
            opcode[0] = opcode[0].upper()
            self.tobe_written_data.append(self.parse(opcode))
        else:
            self.debug('pdo nothing for this line')

    def parse(self, opcode):
        "Does the actual parsing and assembling"

        # hex( (0x1f << 10) ^ (0x0 << 4) ^ 0x1 )
        # returns 0x7c01
        # sample code as supplied by startling

        data_word = []
        output_data = []
        self.debug('pOpcode: ' + str([x for x in opcode]))
        if opcode[0] in ['SET', 'ADD']:
            self.debug("pLine number: " + str(self.line_number))
            #, '\nopcode:', opcode, '\ndata:', str(opcode[1])
            self.debug('pset memory location ' + opcode[1] + ' to '\
                       + opcode[2])
            value_proper = None
            if '$' in opcode[2].upper():
                self.debug('sSirCmpwn; damn you sir!')
            elif opcode[2].upper() in self.ops:
                value_proper = self.ops[opcode[2]]
            elif opcode[2].upper() in self.labels:
                value_proper = 'PASS'
            elif opcode[2].upper() in self.registers:
                value_proper = self.registers[opcode[2].upper()]
            elif '[' in opcode[2] and opcode[2] not in self.registers:
                self.debug("syou're pretty much screwed (opcode[2])")
                value_proper = 'PASS'
            elif '[' in opcode[1] and opcode[1] not in self.registers:
                self.debug("syou're pretty much screwed (opcode[1])")
                opcode[1] = 'P'
            else:
                try:
                    self.debug('snot working: ' + opcode[2] + ' : ' +\
                               self.ops[opcode[2].upper()])
                except KeyError:
                    self.debug('sdefinately not in there')
                value_proper = opcode[2]
                self.debug('svalue_proper: ' + str(value_proper))
                self.debug("slabels: " + str([label for label in self.labels]))
                if value_proper[0:2] != '0x':
                    try:
                        value_proper = hex(int(value_proper)).split('x')[1]
                        self.debug('snow in hex')
                    except TypeError:
                        self.debug('salready in hex')
                else:
                    value_proper = value_proper.split('x')[1]

                # and value_proper[0:2] == '0x':
                if len(str(value_proper)) != 4:
                    self.debug('snot long enough! justifying!')
                    try:
                        value_proper = int(value_proper)
                    except ValueError:
                        pass
                    if type(value_proper) != int:
                        self.debug('svalue_proper: ' + str(value_proper) + \
                                   str(type(value_proper)))
                    value_proper = str(value_proper).rjust(4, '0')
                else:
                    self.debug('sok, value_proper is long enough')

            output_data = [0x1f, (self.registers[opcode[1].upper()]),
                                (self.ops[opcode[0].upper()]), (value_proper)]

            output_data[0] = (output_data[0] << 10)
            output_data[1] = (output_data[1] << 4)
            final = hex(output_data[0] ^ output_data[1] ^ output_data[2])
            data_word.append(final)
            data_word[-1] = data_word[-1].split('x')[1]
            data_word.append(str(output_data[3]))

            self.debug('pdata_word: ' + str(data_word))
            data_word = ''.join(data_word)

            del value_proper



#        elif opcode[0] == 'ADD':
 #           self.debug('pset', opcode[1], 'to', opcode[1], '+', opcode[2])
  #          self.output_file.write(str(self.ops[opcode[0]]))
   #     elif opcode[0] == 'SUB':
    #        self.debug('pset', opcode[1], 'to', opcode[1], '-', opcode[2])
     #       self.output_file.write(str(self.ops[opcode[0]]))
      #  elif opcode[0] == 'MUL':
       #     self.debug('pset', opcode[1], 'to', opcode[1], '*', opcode[2])
        #    self.output_file.write(str(self.ops[opcode[0]]))
#        elif opcode[0] == 'DIV':
 #           self.debug('pset', opcode[1], 'to', opcode[1], '/', opcode[2])
  #          self.output_file.write(str(self.ops[opcode[0]]))
   #     elif opcode[0] == 'MOD':
    #        print '* set', opcode[1], 'to', opcode[1], '%', opcode[2]
     #       self.output_file.write(str(self.ops[opcode[0]]))

        #return output_data
        return data_word

    def print_credits(self):
        "Prints credits!"
        print 'First, notch! Cheers matey!'
        print 'Secondly, startling! For answering my questions!'
        print 'And thirdly, me. For writing the code'

if __name__ == '__main__':
    INST = Assembler()
    INST.print_credits()
    if len(sys.argv) >= 2:
        if sys.argv[1] in ['--help', '-h', '/?']:
            print '\nHeya! Looking for help? Look in the README.md file!'
        elif sys.argv[1] not in ['', None] and sys.argv[2] not in ['', None]:
            INST.load(sys.argv[1], sys.argv[2])
