#!/bin/python
# This is a Quick & Dirty assembler :P
"This is a Quick & Dirty assembler :P"
import re
import logging
import binascii
from io import StringIO
# from pprint import pprint

from .custom_errors import DuplicateLabelError
from .representations import (
    LabelRep,
    CommentRep,
    DirectiveRep,
    DataLiteralRep,
    BasicOpcodeRep,
    SpecialOpcodeRep,
    IncludeDirectiveRep,
)


class Assembler(object):
    "Does the assembling stuff :D"
    def __init__(self, state=None):
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
        }

        self.labels = set()  # {}

        # self.line_number = 0
        self.endianness = 'big'
        self.overwrite = True

        self.debug_toggle = False

        self.log_file = logging.getLogger('Mausembler')
        hdlr = logging.FileHandler('Mausembler.log')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.log_file.addHandler(hdlr)
        self.log_file.setLevel(logging.INFO)

        self.state = {} if not state else state

        BASIC_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<B>(?:0x)?\w+), (?P<A>\w+)\s*(?:;.*)?")
        SPECI_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<A>(?:0x)?\w+)\s*(?:;.*)?")
        LABEL_RE = re.compile(r"\s*:(?P<name>[a-zA-Z0-9]+)\s*(?:;.*)?")
        DIRECTIVE_RE = re.compile(r"\s*\.(?P<name>[a-zA-Z0-9]+)\s*(?P<extra_params>.*)\s*(?:;.*)?")
        COMMENT_RE = re.compile(r"\s*;(?P<content>.*)")

        self.syntax_regex_mapping = [
            (BASIC_OPCODE_RE, self.handle_basic_opcode),
            (SPECI_OPCODE_RE, self.handle_special_opcode),
            (LABEL_RE, self.handle_label),
            (DIRECTIVE_RE, self.handle_directive),
            (COMMENT_RE, self.handle_comment)
        ]

    def debug(self, data):
        "Simple debug function"
        if self.debug_toggle:
            print(data)

    def assemble(self, assembly):
        assembly = self._do_assemble(assembly)
        # pprint(assembly)

        byte_code = self.resolve_machine_code_hex(assembly)
        # print('bytecode;', byte_code)
        # packed_byte_code = self.pack_byte_code(byte_code)
        # return byte_code

    def _do_assemble(self, assembly):
        # format the assembly into a usuable format
        assembly = self.parse(assembly)

        # resolve various specials
        assembly = self.resolve(assembly, DirectiveRep)
        assembly = self.resolve(assembly, LabelRep)

        return assembly

    def resolve_machine_code_hex(self, assembly):
        byte_code = []
        for opcode in assembly:
            hexed = opcode.hexlify()
            assert hexed is not None, (hexed, opcode)
            byte_code.append(hexed)
        return byte_code

    def resolve(self, assembly, of_class):
        changes_to_resolve = True

        # whilst there are parts to resolve
        while changes_to_resolve:
            # record the number of changes this loop

            changes_this_loop = 0
            for index, rep in enumerate(assembly):
                # iterate through the opcodes

                # we are doing stuff in a certain order,
                # so we make sure we are resolving the right types
                if issubclass(rep.__class__, of_class):
                    self.state['assembly'] = assembly
                    result = rep.resolve(self.state)

                    # if something can be resolved
                    if result[0]:
                        # if this opcode resolves to new assembly
                        if result[0] == 'new_assembly':
                            for sub_rep in self._do_assemble(result[1]):
                                assembly.insert(index + 1, sub_rep)
                                changes_this_loop += 1

                        # remove the resolved opcode
                        assembly.pop(index)

            if changes_this_loop == 0:
                changes_to_resolve = False

        if 'assembly' in self.state:
            del self.state['assembly']
        return assembly

    def parse(self, assembly):
        assembly = map(str.rstrip, assembly)

        verified_assembly = []
        for line in assembly:
            for regex, function in self.syntax_regex_mapping:
                match = regex.match(line)
                if match:
                    verified_assembly.append(function(match))
                    break

        return verified_assembly

    def handle_basic_opcode(self, match):
        cur_op = BasicOpcodeRep(
            assembler_ref=self,
            name=match.groupdict()['name'].upper(),
            frag_a=match.groupdict()['A'],
            frag_b=match.groupdict()['B'],
        )
        return cur_op

    def handle_special_opcode(self, match):
        cur_op = SpecialOpcodeRep(
            assembler_ref=self,
            name=match.groupdict()['name'].upper(),
            frag_a=match.groupdict()['A']
        )
        return cur_op

    def handle_directive(self, match):
        name = match.groupdict()['name'].rstrip().upper()
        extra_params = match.groupdict()['extra_params']

        if name == 'INCLUDE':
            return IncludeDirectiveRep(
                assembler_ref=self,
                name=name,
                extra_params=extra_params)
        elif name == 'DAT':
            return DataLiteralRep(
                assembler_ref=self,
                name=name,
                content=extra_params)
        else:
            return DirectiveRep(
                assembler_ref=self,
                name=name,
                extra_params=extra_params)

    def handle_label(self, match):
        name = match.groupdict()['name'].rstrip()
        if name in self.labels:
            raise DuplicateLabelError('{} found twice'.format(name))
        else:
            self.labels.add(name)
        return LabelRep(
            assembler_ref=self,
            name=name)

    def handle_comment(self, match):
        return CommentRep(
            assembler_ref=self,
            content=match.groupdict()['content'])

    def hex_to_file(self, hex_list):
        temp_file = StringIO()
        for line in hex_list:
            self.debug('\tline: ' + line)
            temp_file.write(binascii.a2b_hex(line))

        return temp_file

    def assemble_opcode(self, opcode):
        "Does the actual parsing and assembling"

        # hex( (0x1f << 10) ^ (0x0 << 4) ^ 0x1 )
        # returns 0x7c01
        # sample code as supplied by startling

        # hex(0x7c<<24 ^ 0x2<<20 ^ 0x1<<16 ^ 0x1)
        # returns 0x7c11f888
        # my own (revised) reference code

        self.debug('Opcode: {}'.format(opcode))

        # In bits (in LSB-0 format), a basic instruction has the format: aaaaaabbbbbooooo
        # will take the next word literally, unless otherwise specified
        if opcode.attrs['name'] in self.basic_opcodes.keys():
            self.debug('perform {} operation with {} and {}'.format(
                opcode.attrs['name'], opcode.attrs['frag_b'], opcode.attrs['frag_a']))

            print('opcode:', opcode)
            assert opcode.attrs['name'] in self.basic_opcodes
            opcode_val = self.basic_opcodes[opcode.attrs['name']]

            opcode_frag_b = opcode.attrs['frag_b']
            opcode_frag_b = self.resolve_frag(opcode_frag_b)

            opcode_frag_a = opcode.attrs['frag_a']
            opcode_frag_a = self.resolve_frag(opcode_frag_a)

            print(
                hex(opcode_val),
                hex(opcode_frag_b),
                hex(opcode_frag_b))

        #     word = 0

            output_data = []
            output_data[0] = int(output_data[0]) << 26
            output_data[1] = int(output_data[1]) << 20
            output_data[2] = int(output_data[2]) << 16
            output_data[3] = int(output_data[3])

        #     print('output_data:', [hex(q) for q in output_data])

            final = (output_data[0] ^ output_data[1])
            final = (final ^ output_data[2])
            final = (final ^ output_data[3])
        #     final = hex(final)
        #     print('type:', type(final))
        #     final = final.strip('L')

        #     if self.strd(final):
        #         print('final:', hex(int(final, 16)))
        #     else:
        #         print('final:', hex(int(final)))

        # Special opcodes always have their lower five bits unset, have one value and a
        # five bit opcode. In binary, they have the format: aaaaaaooooo00000
        # return data_word

    def resolve_frag(self, frag):
        if frag[0:2] == '0b':
            frag = int(frag, 2)
        elif frag[0:2] == '0x':
            frag = int(frag, 16)

        elif frag.upper() in self.values:
            frag = self.values[frag.upper()]

        return frag

'''Report mausembler bugs to <https://github.com/Mause/Mausembler/issues>
Email me: jack.thatch@gmail.com
'''
