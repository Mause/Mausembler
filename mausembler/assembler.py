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


class Assembler:
    "Does the assembling stuff :D"
    def __init__(self):
        self.basic_opcodes = {
            'SET': 0x01, 'ADD': 0x02, 'SUB': 0x03,
            'MUL': 0x04, 'MLI': 0x05, 'DIV': 0x06,
            'DVI': 0x07, 'MOD': 0x08, 'MDI': 0x09,
            'AND': 0x0a, 'BOR': 0x0b, 'XOR': 0x0c,
            'ASR': 0x0e, 'SHL': 0x0f, 'IFB': 0x10,
            'IFC': 0x11, 'IFE': 0x12, 'IFN': 0x13,
            'IFG': 0x14, 'IFA': 0x15, 'IFL': 0x16,
            'IFU': 0x17, 'NON': 0x18, 'NON': 0x19,
            'ADX': 0x1a, 'SBX': 0x1b, 'NON': 0x1c,
            'NON': 0x1d, 'STI': 0x1e, 'STD': 0x1f}
            # 'DAT':0x}
        self.special_opcodes = {
            'NON': 0x00, 'JSR': 0x01, 'NON': 0x02, 'NON': 0x03,
            'NON': 0x04, 'NON': 0x05, 'NON': 0x06, 'HCF': 0x07,
            'INT': 0x08, 'IAG': 0x09, 'IAS': 0x0a, 'IAP': 0x0b,
            'NON': 0x0c, 'NON': 0x0d, 'NON': 0x0e, 'NON': 0x0f,
            'HWN': 0x10, 'HQN': 0x11, 'HWI': 0x12, 'NON': 0x13,
            'NON': 0x14, 'NON': 0x15, 'NON': 0x16, 'NON': 0x17,
            'NON': 0x18, 'NON': 0x19, 'NON': 0x1a, 'NON': 0x1b,
            'NON': 0x1c, 'NON': 0x1d, 'NON': 0x1e, 'NON': 0x1f}
        self.values = {
            'A': 0x00, 'B': 0x01,
            'C': 0x02, 'X': 0x03,
            'Y': 0x04, 'Z': 0x05,
            'I': 0x06, 'J': 0x07,
            '[A]': 0x08, '[B]': 0x09,
            '[C]': 0x0a, '[X]': 0x0b,
            '[Y]': 0x0c, '[Z]': 0x0d,
            '[I]': 0x0e, '[J]': 0x0f,
            # 0x10-0x17: [next word + register] goes here
            'POP': 0x18, '[SP++]': 0x18,
            'PUSH': 0x18, '[--SP': 0x18,
            'PEEK': 0x19, '[SP]': 0x19,
            '[SP+[PC++]]': 0x1a, '[--SP]': 0x1a,
            'SP': 0x1b, 'PC': 0x1c,
            'EX': 0x1d, '[PC++]': 0x1e,
            'PC++': 0x1f,
            # up and coming - stuff i dont know what to do with
            'NON': 0x20, 'NON': 0x21,
            'NON': 0x22, 'NON': 0x23,
            'NON': 0x24, 'NON': 0x25,
            'NON': 0x26, 'NON': 0x27,
            'NON': 0x28, 'NON': 0x29,
            'NON': 0x2a, 'NON': 0x2b,
            'NON': 0x2c, 'NON': 0x2d,
            'NON': 0x2e, 'NON': 0x2f,
            'NON': 0x30, 'NON': 0x31,
            'NON': 0x32, 'NON': 0x33,
            'NON': 0x34, 'NON': 0x35,
            'NON': 0x36, 'NON': 0x37,
            'NON': 0x38, 'NON': 0x39,
            'NON': 0x3a, 'NON': 0x3b,
            'NON': 0x3c, 'NON': 0x3d,
            'NON': 0x3e, 'NON': 0x3f}
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
        self.endian = 'big'
        # set the instance.debug_toggle
        # switch for debug info
        self.debug_toggle = False
        print "Mausembler; self-titled!\n"

    def debug(self, data):
        "Simple debug function"
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
        self.dep_path.append(os.sep.join(abspath.split(os.sep)[:-1]))
        del abspath
        self.debug('pself.dep_path: ' + str(self.dep_path))
        cur_input_filename = input_filename

        if os.path.exists(os.getcwd() + os.sep + input_filename):
            input_filename = os.getcwd() + os.sep + input_filename

        for num in range(len(self.dep_path)):
            possibles = [(self.dep_path[num] + os.sep + cur_input_filename),
                         (self.dep_path[num] + os.sep +
                          cur_input_filename.split(os.sep)[-1]),
                         (os.getcwd() + os.sep + self.dep_path[num]
                          + os.sep + cur_input_filename),
                         (os.getcwd() + os.sep + self.dep_path[num]
                          + os.sep + cur_input_filename.split(os.sep)[-1])]
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
            self.debug(
                'pOkay. The input_filename variable is empty. NOT HELPFUL')
            self.debug('pthe cpu will be told to')
        else:
            self.debug('pfor "' + self.input_filename
                       + '" the cpu will be told to;')

        # this is the second loop; it'll do the actual assembling
        for opcode in self.conditioned_data:
            str(self.go_parse(opcode))
        if len(self.dependencies) != 0:
            self.debug('pDependencies: ' + str(self.dependencies))
        else:
            self.debug('''pThe input file was not found
to depend on any external code bases''')
        if len(self.labels) != 0:
            self.debug('pLabels: ' + str([label for label in self.labels]))
        else:
            self.debug('pNo labels were found in the input file')
        self.debug('pAbout to write output data to "' + output_filename + '"')
        errors = 0
        total_lines = 0
        for line in range(len(self.tobe_written_data)):
            print line-len(self.tobe_written_data)
            line = self.tobe_written_data[line-len(self.tobe_written_data)]
            if line != '' and line != () and line != []:
                self.debug('pline: ' + line)
                print 'line:', line
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
            print (str(errors) + ' out of '
                   + str(total_lines) + ' parseable lines threw errors')
            self.log_file.info(
                str(errors) + ' out of '
                + str(total_lines) + ' parseable lines threw errors')
        print '\nDone\n'
        self.log_file.info('Done')

        #self.output_file.close()

    def do_dependencies(self, data):
        """Simply loops through each line in the file,
        and determines which files the file depends on"""
        # This function sounds good, in theory,
        # but in reality it won't work for
        # dependencies that have dependencies
        # themselves
        self.debug("pDetermining dependencies...")
        if data not in self.data_done:
            self.data_done.append(data)
        else:
            return
        for line in data:
            if line[0] == '.':
                if line.split()[0] == '.include':
                    self.dependencies.append(
                        ''.join(ch for ch in (line.split()[1:])
                                if ch not in "\"'<>"))

        self.debug('pdeps ' + str(self.dep_path))

        for dep in self.dependencies:
            for num in range(len(self.dep_path)):
                possibles = [(self.dep_path[num] + os.sep + dep),
                             (self.dep_path[num] + os.sep +
                              dep.split(os.sep)[-1]),
                             (os.getcwd() + os.sep + self.dep_path[num]
                              + os.sep + dep),
                             (os.getcwd() + os.sep + self.dep_path[num]
                              + os.sep + dep.split(os.sep)[-1])]
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
                    self.debug('premember line ' + str(self.line_number) +
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
                    self.debug('premember line ' + str(self.line_number)
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

        # hex(0x7c<<24 ^ 0x2<<20 ^ 0x1<<16 ^ 0x1)
        # returns 0x7c11f888
        # my own (revised) reference code

        data_word = []
        output_data = []
        self.debug('pOpcode: ' + str([x for x in opcode]))

#        self.debug('p'+str([type(x) for x in opcode]))
        part_b_primary = 0x1f  # will take the next word literally, unless otherwise specified
        if opcode[0] in self.basic_opcodes.keys():
            self.debug("pLine number: " + str(self.line_number))
            self.debug('pperform ' + opcode[0].upper() + ' operation with ' +
                       opcode[1].upper() + ' and ' + opcode[2].upper())
            opcodewk = opcode
            del opcode
            opcode_out_data = []
            print 'opcodewk:', opcodewk
            for opcodesub in opcodewk:
                if '$' in opcodesub.upper():
                    print 'SirCmpwn is up to his old tricks again'
                elif opcodesub.upper() in self.basic_opcodes.keys():
                    opcodesub = self.basic_opcodes[opcodesub]
                elif opcodesub.upper() in self.labels.keys():
                    opcodesub = 'PASS'
                elif opcodesub.upper() in self.values.keys():
                    opcodesub = self.values[opcodesub.upper()]
                elif [opcodesub[0], opcodesub[-1]] == ['[', ']']:
                    part_b_primary = 0x1e  # okay, gonna tell the cpu to interpret
                                           # the next word as a pointer
                    if opcodesub[1:-1][:2] == '0x':
                        opcodesub = opcodesub[1:-1]
                    else:
                        opcodesub = 'PASS'
#                elif opcodesub.upper() == '[A+1]':
                    
                elif '[' in opcodesub and opcodesub not in self.values:
                    self.debug("syou're pretty much screwed (opcode[2])")
                    opcodesub = 'P'
                else:
                    if opcodesub[0:2] == '0b':
                        opcodesub = int(opcodesub[2:], 2)
                    try:
                        self.debug('snot working: ' + str(opcodesub) + ' : ' +
                                   self.basic_opcodes[str(opcodesub).upper()])
                    except KeyError:
                        self.debug('sdefinately not in there')
                    self.debug("slabels: " +
                               str([label for label in self.labels]))
                    if str(opcodesub)[0:2] != '0x':
                        try:
                            self.debug('stry: '+str(type(opcodesub)))
                            opcodesub = hex(int(opcodesub))#.split('x')[1]
                            self.debug('snow in hex: '+str(type(opcodesub)))
                        except TypeError:
                            self.debug('salready in hex')
                        except ValueError:
                            self.debug('''seither error in users program,
or something was not caught''')
                    else:
                        opcodesub = opcodesub#.split('x')[1]
            
                if self.strd(opcodesub): print 'opcodesub:', hex(int(opcodesub, 16))
                else: print 'opcodesub:', hex(int(opcodesub))
                opcode_out_data.append(opcodesub)

            print 'opcode_out_data:', opcode_out_data
            
            output_data.append(opcode_out_data[0])
            output_data.append(opcode_out_data[1])
            output_data.append(opcode_out_data[2])

            output_data = [hex(int(part_b_primary))] + output_data

 #           except TypeError:
  #              print output_data
#            print 'output_data:', output_data
 #           print 'output_data:'
  #          for thing in range(len(output_data)):
   #             try:
    #                if type(output_data[thing]) == str: print hex(int(output_data[thing], 16))
     #               else: print hex(int(output_data[thing]))
      #              output_data[thing] = hex(int(output_data[thing], 16))
       #         except (TypeError, ValueError):
        #            print 'errored', output_data[thing]

#            print 'output_data:', output_data
 #           print 'output_data:', [type(x) for x in output_data]
  #          print 'output_data[0]:', type(output_data[0])
            # hex(0x7c<<24 ^ 0x2<<20 ^ 0x1<<16 ^ 0x1)
            if self.strd(output_data[0]): output_data[0] = int(output_data[0], 16)<<26
            else: output_data[0] = int(output_data[0])<<26
            if self.strd(output_data[1]): output_data[1] = int(output_data[1], 16)<<20
            else: output_data[1] = int(output_data[1])<<20
            if self.strd(output_data[2]): output_data[2] = int(output_data[2], 16)<<16
            else: output_data[2] = int(output_data[2])<<16
            if self.strd(output_data[3]): output_data[3] = int(output_data[3], 16)
            else: output_data[3] = int(output_data[3])

            print 'output_data:', [hex(x) for x in output_data]
            

#            print 'output_data:', [type(x) for x in output_data]
            
            final = (output_data[0] ^ output_data[1])
            final = (final ^ output_data[2])
            final = (final ^ output_data[3])
            final = hex(final)
            print 'type:', type(final)
            final = final.strip('L')

            if self.strd(final): print 'final:', hex(int(final,16))
            else: print 'final:', hex(int(final))

            
            data_word.append(final)
            #data_word[-1] = data_word[-1].split('x')[1]
            data_word[-1] = data_word[-1].split('x')[1]            
      #      data_word.append(str(output_data[3]))

            self.debug('pdata_word: ' + str(data_word))
            data_word = ''.join(data_word)
            print 
        return data_word
    def strd(self, item):
        return type(item) == str

    def print_credits(self):
        "Prints credits!"
        print 'First, notch! Cheers matey!'
        print 'Secondly, startling! For answering my questions!'
        print 'And thirdly, me. For writing the code'

help_data='''\
Usage: mausembler.py [OPTIONS]... SOURCE DEST
Assemble SOURCE to DEST

Mandatory arguments to long options are mandatory for short options too.
  -b, --big-endian             write the bytes in big endian order
  -l, --little-endian          write the bytes in little endian order
      --credits                shows credits

Report mausembler bugs to <https://github.com/Mause/Mausembler/issues>
Email me: jack.thatch@gmail.com\
'''

#      --version  output version information and exit
#  -o, --overwrite              overwrite any existing files

if __name__ == '__main__':
    if sys.argv[-1] in ['--help', '-h', '/?']: print help_data
    else:
        
        if '--credits' in sys.argv:
            INST = Assembler()
            print 'Mausembler; self-titled!'
            INST.print_credits()
        elif len(sys.argv) not in [1,2]:
            INST = Assembler()
            for x in sys.argv[1:]:
                if x == '--debug': INST.debug_toggle = True
                if x == '--big-endian' and '--little-endian' not in sys.argv[1:]: INST.endian = 'big'
                elif x == '--little-endian' and '--big-endian' not in sys.argv[1:]: INST.endian = 'little'
                if sys.argv[1] not in ['', None] and sys.argv[2] not in ['', None]:
                    INST.load(sys.argv[1], sys.argv[2])
        else:
            print "mausembler: missing operands\nTry 'mv --help' for more information."

