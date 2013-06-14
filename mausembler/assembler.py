#!/bin/python
# This is a Quick & Dirty assembler :P
"This is a Quick & Dirty assembler :P"
import re
import struct
import logging
# from pprint import pprint

from .custom_errors import DuplicateLabelError, DASMSyntaxError
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
        self.labels = {}

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

        BASIC_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<B>(?:0x|0b)?(?:\d+|\w+)),? (?P<A>(?:0x|0b)?(?:\d+|\w+))\s*(?:;.*)?")
        SPECI_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<A>(?:0x|0b)?(?:\d+|\w+))'                              '\s*(?:;.*)?")
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
        logging.info(data)

    def assemble(self, assembly):
        self.debug('Parsing base file')
        assembly = self._do_assemble(assembly)

        self.debug('Resolving parsed assembly into hex')
        self.state['assembly'] = assembly
        byte_code = self.resolve_machine_code_hex(assembly)
        del self.state['assembly']

        self.debug('Packing hex')
        packed_byte_code = self.pack_byte_code(byte_code)

        return packed_byte_code

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
            hexed = opcode.hexlify(self.state)

            if not isinstance(opcode, LabelRep) and not isinstance(opcode, CommentRep):
                assert hexed is not None, (hexed, opcode)
                byte_code.append(hexed)

        return byte_code

    def resolve(self, assembly, of_class):
        changes_to_resolve = True

        # whilst there are parts to resolve
        while changes_to_resolve:
            # record the number of changes this loop
            changes_this_loop = 0

            # iterate through the opcodes
            for index, rep in enumerate(assembly):

                # we are doing stuff in a certain order,
                # so we make sure we are resolving the right types
                if issubclass(rep.__class__, of_class):
                    # self.state['assembly'] = assembly
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

        # if 'assembly' in self.state:
        #     del self.state['assembly']
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
            else:
                raise DASMSyntaxError(line)

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
            self.labels[name] = None

        return LabelRep(
            assembler_ref=self,
            name=name)

    def handle_comment(self, match):
        return CommentRep(
            assembler_ref=self,
            content=match.groupdict()['content'])

    def pack_byte_code(self, hex_list):
        """
        Outputs hex to file
        used http://stackoverflow.com/a/3855178/1433288 for reference
        """
        fmt = '{}L'.format(len(hex_list))
        if self.endianness == 'little':
            fmt = '<' + fmt
        else:
            fmt = '>' + fmt

        return struct.pack(fmt, *hex_list)
