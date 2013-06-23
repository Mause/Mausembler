#!/bin/python
# This is a Quick & Dirty assembler :P
"This is a Quick & Dirty assembler :P"
import re
import sys
import struct
import logging
# from pprint import pprint

from .definitions import values, special_opcodes, basic_opcodes
from .custom_errors import (
    DuplicateLabelError,
    DASMSyntaxError,
    ReservedKeyword,
    UnknownDirective
)
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
    def __init__(self, state=None, verbosity=None, endianness=None):
        "performs initalisation"
        self.labels = {}

        # process args
        self.verbosity = logging.INFO if verbosity is None else verbosity
        self.endianness = 'little' if endianness is None else endianness
        self.state = state if state else {}

        # setup logging
        self.log_file = logging.getLogger('Mausembler')
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

        hdlr = logging.FileHandler('Mausembler.log')
        hdlr.setFormatter(formatter)
        self.log_file.addHandler(hdlr)

        if verbosity is not None:
            stdout_hdlr = logging.StreamHandler(sys.stdout)
            stdout_hdlr.setFormatter(formatter)
            self.log_file.addHandler(stdout_hdlr)

        self.log_file.setLevel(self.verbosity)

        # setup the regex's
        BASIC_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<B>(?:0x|0b)?(?:\d+|[/*-+\[\]\w]+)),? (?P<A>(?:0x|0b)?(?:\d+|[/*-+\[\]\w]+))\s*(?:;.*)?")
        SPECI_OPCODE_RE = re.compile(r"\s*(?P<name>[a-zA-Z]{3}) (?P<A>(?:0x|0b)?(?:\d+|[/*-+\[\]\w]+))"                                      r"\s*(?:;.*)?")
        LABEL_RE = re.compile(r"\s*:(?P<name>[a-zA-Z0-9\_\-]+)\s*(?:;.*)?")
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

    def assemble(self, assembly, filename='base_file'):
        "assembles the provided assembly"
        # parse the provided assembly into objects
        self.log_file.info('Parsing and resolving base file')
        assembly = self._parse_and_resolve(assembly, filename)

        # resolve the assembly into hex
        self.log_file.info('Resolving parsed assembly into hex')
        self.state['assembly'] = assembly
        byte_code = self.resolve_machine_code_hex(assembly)
        del self.state['assembly']

        # and pack that hex into a single bytestring
        self.log_file.info('Packing hex')
        packed_byte_code = self.pack_byte_code(byte_code)

        return packed_byte_code

    def _parse_and_resolve(self, assembly, filename=None):
        "parses and resolves provided assembly into base assembly"
        # format the assembly into a usuable format

        self.log_file.debug('Parsing...')
        assembly = self.parse(assembly, filename)

        # resolve various specials
        self.log_file.debug('Resolving DirectiveRep\'s')
        assembly = self.resolve(assembly, DirectiveRep, filename)

        self.log_file.debug('Resolving LabelRep\'s')
        assembly = self.resolve(assembly, LabelRep, filename)

        # resolve those that remain... there shouldn't be any, but w/e
        self.log_file.debug('Resolving misc\'s')
        assembly = self.resolve(assembly, object, filename)

        return assembly

    def resolve_machine_code_hex(self, assembly):
        "resolves all provided assembly objects into their hex representation"
        exclude = {LabelRep, CommentRep}

        byte_code = (
            opcode.hexlify(self.state)
            for opcode in assembly
            if type(opcode) not in exclude
        )

        return list(byte_code)

    def resolve(self, assembly, of_class, filename):
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
                    result = rep.resolve(self.state, filename)

                    # if something can be resolved
                    if result:
                        # if this opcode resolves to new assembly
                        if 'new_assembly' in result:
                            for sub_rep in self._parse_and_resolve(result['new_assembly'], result['filename']):
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

    def parse(self, assembly, filename=None):
        "runs all regex's against provided assembly"
        # filter out extra whitespace and empty lines
        assembly = map(str.rstrip, assembly)

        verified_assembly = []
        for line_number, line in enumerate(assembly):
            if not line:
                continue
            else:
                self.log_file.debug('{}. {}'.format(line_number + 1, line))

            # check a regex against each line of assembly
            for regex, function in self.syntax_regex_mapping:
                match = regex.match(line)

                if match:
                    # if one matches, run the specified function against the match
                    # self.log_file.debug('"{}" matched for function {}'.format(
                    #     line, function.__name__))
                    verified_assembly.append(
                        function(match, line_number + 1, filename))
                    break
            else:
                # if none of the regex's match, throw an error
                raise DASMSyntaxError(line)

        return verified_assembly

    def handle_basic_opcode(self, match, line_number, filename):
        "grab info from match and create a BasicOpcodeRep object"
        cur_op = BasicOpcodeRep(
            assembler_ref=self,
            line_number=line_number,
            filename=filename,
            name=match.groupdict()['name'].upper(),
            frag_a=match.groupdict()['A'],
            frag_b=match.groupdict()['B'],
        )
        return cur_op

    def handle_special_opcode(self, match, line_number, filename):
        "grab info from match and create a SpecialOpcodeRep object"
        cur_op = SpecialOpcodeRep(
            assembler_ref=self,
            line_number=line_number,
            filename=filename,
            name=match.groupdict()['name'].upper(),
            frag_a=match.groupdict()['A']
        )
        return cur_op

    def handle_directive(self, match, line_number, filename):
        """grabs info from match,
        determines what kind of directive it is,
        then returns the appropriate object"""

        name = match.groupdict()['name'].rstrip().upper()
        extra_params = match.groupdict()['extra_params']

        if name == 'INCLUDE':
            return IncludeDirectiveRep(
                assembler_ref=self,
                line_number=line_number,
                filename=filename,
                name=name,
                extra_params=extra_params)
        elif name == 'DAT':
            return DataLiteralRep(
                assembler_ref=self,
                line_number=line_number,
                filename=filename,
                name=name,
                content=extra_params)
        else:
            raise UnknownDirective("{} on line {} of file \"{}\"".format(
                name,
                line_number,
                filename))
            # return DirectiveRep(
            #     assembler_ref=self,
            #     name=name,
            #     extra_params=extra_params)

    def handle_label(self, match, line_number, filename):
        "grab info from match and create a LabelRep object"
        name = match.groupdict()['name'].rstrip()

        if name in values or name in special_opcodes or name in basic_opcodes:
            raise ReservedKeyword(name)

        if name in self.labels:
            raise DuplicateLabelError(
                '{} found twice. '
                'First time on line {} of "{}", '
                'second on line {} of "{}"'.format(
                    name,
                    self.labels[name]['line_number'],
                    self.labels[name]['filename'],
                    line_number,
                    filename))
        else:
            self.labels[name] = {
                'filename': filename,
                'line_number': line_number,
                'address': None
            }

        return LabelRep(
            assembler_ref=self,
            line_number=line_number,
            filename=filename,
            name=name)

    def handle_comment(self, match, line_number, filename):
        "grab info from match and create a CommentRep object"
        return CommentRep(
            assembler_ref=self,
            line_number=line_number,
            filename=filename,
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
