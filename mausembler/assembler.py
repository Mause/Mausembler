#!/bin/python
# This is a Quick & Dirty assembler :P
"This is a Quick & Dirty assembler :P"
import re
import sys
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
    def __init__(self, state=None, debug_toggle=None, endianness=None):
        "performs initalisation"
        self.labels = {}

        # process args
        self.debug_toggle = debug_toggle if debug_toggle is not None else False
        self.endianness = endianness if endianness is not None else 'little'
        self.state = {} if not state else state

        # setup logging
        self.log_file = logging.getLogger('Mausembler')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

        hdlr = logging.FileHandler('Mausembler.log')
        hdlr.setFormatter(formatter)
        self.log_file.addHandler(hdlr)

        if debug_toggle:
            stdout_hdlr = logging.StreamHandler(sys.stdout)
            stdout_hdlr.setFormatter(formatter)
            self.log_file.addHandler(stdout_hdlr)

        self.log_file.setLevel(logging.INFO)

        # setup the regex's
        BASIC_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<B>(?:0x|0b)?(?:\d+|\w+)),? (?P<A>(?:0x|0b)?(?:\d+|\w+))\s*(?:;.*)?")
        SPECI_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<A>(?:0x|0b)?(?:\d+|\w+))'                             '\s*(?:;.*)?")
        LABEL_RE = re.compile(r"\s*:(?P<name>[a-zA-Z0-9]+)\s*(?:;.*)?")
        DIRECTIVE_RE = re.compile(r"\s*\.(?P<name>[a-zA-Z0-9]+)\s*(?P<extra_params>.*)\s*(?:;.*)?")
        COMMENT_RE = re.compile(r"\s*;(?P<content>.*)")

        # map the regex's to processing functions
        self.syntax_regex_mapping = [
            (BASIC_OPCODE_RE, self.handle_basic_opcode),
            (SPECI_OPCODE_RE, self.handle_special_opcode),
            (LABEL_RE, self.handle_label),
            (DIRECTIVE_RE, self.handle_directive),
            (COMMENT_RE, self.handle_comment)
        ]

    def assemble(self, assembly):
        "assembles the provided assembly"
        # parse the provided assembly into objects
        self.log_file.info('Parsing base file')
        assembly = self._do_assemble(assembly)

        # resolve the assembly into hex
        self.log_file.info('Resolving parsed assembly into hex')
        self.state['assembly'] = assembly
        byte_code = self.resolve_machine_code_hex(assembly)
        del self.state['assembly']

        # and pack that hex into a single bytestring
        self.log_file.info('Packing hex')
        packed_byte_code = self.pack_byte_code(byte_code)

        return packed_byte_code

    def _do_assemble(self, assembly):
        "parses and resolves provided assembly into base assembly"
        # format the assembly into a usuable format
        assembly = self.parse(assembly)

        # resolve various specials
        assembly = self.resolve(assembly, DirectiveRep)
        assembly = self.resolve(assembly, LabelRep)

        # resolve those that remain... there shouldn't be any, but w/e
        assembly = self.resolve(assembly, object)

        return assembly

    def resolve_machine_code_hex(self, assembly):
        "resolves all provided assembly objects into their hex representation"
        exclude = {LabelRep, CommentRep}

        assembly = (
            opcode
            for opcode in assembly
            if type(opcode) not in exclude
        )

        byte_code = (
            opcode.hexlify(self.state)
            for opcode in assembly
        )

        return list(byte_code)

    def resolve(self, assembly, of_class):
        "iterates through assembly, filtering by of_class, and resolves everything"
        changes_to_resolve = True

        # whilst there are parts to resolve
        while changes_to_resolve:
            # record the number of changes this loop
            changes_this_loop = False

            # iterate through the opcodes
            for index, rep in enumerate(assembly):

                # we are doing stuff in a certain order,
                # so we make sure we are resolving the right types
                if issubclass(rep.__class__, of_class):
                    result = rep.resolve(self.state)

                    # if something can be resolved
                    if result and result[0]:
                        # if this opcode resolves to new assembly
                        if result[0] == 'new_assembly':
                            for sub_rep in self._do_assemble(result[1]):
                                # loop through the new assembly,
                                # and insert it all after the current opcode
                                assembly.insert(index + 1, sub_rep)
                                changes_this_loop = True

                        # remove the resolved opcode
                        assembly.pop(index)

            if not changes_this_loop:
                # if there weren't any changes this loop, consider everything that can
                # be resolved resolved, and exit the loop
                changes_to_resolve = False

        return assembly

    def parse(self, assembly):
        "runs all regex's against provided assembly"
        # filter out extra whitespace and empty lines
        assembly = map(str.rstrip, assembly)
        assembly = filter(bool, assembly)

        verified_assembly = []
        for line in assembly:
            # check a regex against each line of assembly
            for regex, function in self.syntax_regex_mapping:
                match = regex.match(line)
                if match:
                    # if one matches, run the specified function against the match
                    verified_assembly.append(function(match))
                    break
            else:
                # if none of the regex's match, throw an error
                raise DASMSyntaxError(line)

        return verified_assembly

    def handle_basic_opcode(self, match):
        "grab info from match and create a BasicOpcodeRep object"
        cur_op = BasicOpcodeRep(
            assembler_ref=self,
            name=match.groupdict()['name'].upper(),
            frag_a=match.groupdict()['A'],
            frag_b=match.groupdict()['B'],
        )
        return cur_op

    def handle_special_opcode(self, match):
        "grab info from match and create a SpecialOpcodeRep object"
        cur_op = SpecialOpcodeRep(
            assembler_ref=self,
            name=match.groupdict()['name'].upper(),
            frag_a=match.groupdict()['A']
        )
        return cur_op

    def handle_directive(self, match):
        """grabs info from match,
        determines what kind of directive it is,
        then returns the appropriate object"""

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
            raise Exception('Unknown Directive: {}'.format(name))
            # return DirectiveRep(
            #     assembler_ref=self,
            #     name=name,
            #     extra_params=extra_params)

    def handle_label(self, match):
        "grab info from match and create a LabelRep object"
        name = match.groupdict()['name'].rstrip()
        if name in self.labels:
            raise DuplicateLabelError('{} found twice'.format(name))
        else:
            self.labels[name] = None

        return LabelRep(
            assembler_ref=self,
            name=name)

    def handle_comment(self, match):
        "grab info from match and create a CommentRep object"
        return CommentRep(
            assembler_ref=self,
            content=match.groupdict()['content'])

    def pack_byte_code(self, hex_list):
        """
        Outputs hex to file
        used http://stackoverflow.com/a/3855178/1433288 for reference
        """
        # determine how big it should be
        fmt = '{}L'.format(len(hex_list))

        # set endianness
        if self.endianness == 'little':
            fmt = '<' + fmt
        else:
            fmt = '>' + fmt

        # pack hex
        return struct.pack(fmt, *hex_list)
