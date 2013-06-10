import os
import re
import logging

from .definitions import basic_opcodes, values


class ReferenceRep(object):
    pass


class Expression(object):
    def __init__(self, expr):
        self.HEX_RE = re.compile(r'(0x\d+)')
        self.BIN_RE = re.compile(r'(0b[01]+)')

    def resolve(self):
        return 'new_assembly'


class Rep(object):
    def __init__(self, assembler_ref, **kwargs):
        self.assembler_ref = assembler_ref
        self.attrs = kwargs

    def size(self):
        raise NotImplementedError()

    def hexlify(self):
        # this doesn't strictly have to return anything
        return None

    def resolve(self, state):
        # this is used for special actions, such as opcodes or instructions
        # that expand out into more opcodes
        # atm, the only action implemented is 'new_assembly'
        return None, None


class CommentRep(Rep):
    def __repr__(self):
        return "<Comment: {}>".format(self.attrs['content'])


class LabelRep(Rep):
    def size(self):
        return 0

    def __repr__(self):
        return "<Label: {}>".format(self.attrs['name'])


class OpcodeRep(Rep):
    REF_RE = re.compile(r'\[(?P<ref_content>.*)\]')
    debug_toggle = True

    def debug(self, data):
        "Simple debug function"
        if self.debug_toggle:
            print(data)
        logging.info(data)

    def resolve_frag(self, frag):
        if frag[0:2] == '0b':
            frag = int(frag, 2)
        elif frag[0:2] == '0x':
            frag = int(frag, 16)

        elif frag.upper() in values:
            frag = values[frag.upper()]

        return frag

    def assemble_opcode(self, opcode):
        "Does the actual parsing and assembling"

        # hex( (0x1f << 10) ^ (0x0 << 4) ^ 0x1 )
        # returns 0x7c01
        # sample code as supplied by startling

        # hex(0x7c<<24 ^ 0x2<<20 ^ 0x1<<16 ^ 0x1)
        # returns 0x7c11f888
        # my own (revised) reference code

        self.debug('Opcode: {}'.format(opcode))

        # In bits (in LSB-0 format), a basic instruction has the format:
            # aaaaaabbbbbooooo
        # will take the next word literally, unless otherwise specified
        if opcode.attrs['name'] in basic_opcodes.keys():
            self.debug('perform {} operation with {} and {}'.format(
                opcode.attrs['name'],
                opcode.attrs['frag_b'],
                opcode.attrs['frag_a']))

            print('opcode:', opcode)
            assert opcode.attrs['name'] in basic_opcodes
            opcode_val = basic_opcodes[opcode.attrs['name']]

            opcode_frag_b = opcode.attrs['frag_b']
            opcode_frag_b = self.resolve_frag(opcode_frag_b)

            opcode_frag_a = opcode.attrs['frag_a']
            opcode_frag_a = self.resolve_frag(opcode_frag_a)

            # print(
            #     opcode_val,
            #     opcode_frag_b,
            #     opcode_frag_a)

            # print(opcode_val, type(opcode_val))
            # opcode_val = int(opcode_val, 16)
            # opcode_frag_b = int(opcode_frag_b, 16)
            # opcode_frag_a = int(opcode_frag_a, 16)

            # print(
            #     hex(opcode_val),
            #     hex(opcode_frag_b),
            #     hex(opcode_frag_a))

            output_data = [0x1f, opcode_val, opcode_frag_b, opcode_frag_a]
            output_data[0] = int(output_data[0]) << 26
            output_data[1] = int(output_data[1]) << 20
            output_data[2] = int(output_data[2]) << 16
            output_data[3] = int(output_data[3])

        #     print('output_data:', [hex(q) for q in output_data])

            final = (output_data[0] ^ output_data[1])
            final = (final ^ output_data[2])
            final = (final ^ output_data[3])
            print('final:', hex(final))
            # final = hex(final)
        #     print('type:', type(final))
        #     final = final.strip('L')

        #     if self.strd(final):
        #         print('final:', hex(int(final, 16)))
        #     else:
        #         print('final:', hex(int(final)))

        # Special opcodes always have their lower five bits unset,
        # have one value and a five bit opcode.
        # In binary, they have the format: aaaaaaooooo00000

        return final


class BasicOpcodeRep(OpcodeRep):
    contains_reference = False

    def __repr__(self):
        return "<BasicOpcobe: {} {} {}>".format(
            self.attrs['name'],
            self.attrs['frag_b'],
            self.attrs['frag_a'])

    def hexlify(self):
        # TODO: add code here to resolve label references

        # if self.REF_RE.match(self.frag_a):
        #     if re.match(self.frag_a)

        # self.assembler_ref

        assert not self.contains_reference
        h = self.assemble_opcode(self)
        assert h, h
        return h

    def resolve(self, state):
        pass


class SpecialOpcodeRep(OpcodeRep):
    def __repr__(self):
        return "<SpecialOpcode: {} {}>".format(
            self.attrs['name'],
            self.attrs['frag_a'])


class DirectiveRep(Rep):
    def size(self):
        return 0

    def __repr__(self):
        extra_params = (
            self.attrs['extra_params'] if self.attrs['extra_params']
            else "{}")
        return "<{} {}>".format(
            self.attrs['name'],
            extra_params)


class IncludeDirectiveRep(DirectiveRep):
    def resolve(self, state):
        "Loads an included file"

        filename = self.attrs['extra_params'].rstrip()
        if not os.path.exists(filename):
            filename = os.path.join(state['input_directory'], filename)

        try:
            with open(filename) as dep_handler:
                return 'new_assembly', dep_handler.readlines()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                'Loading include failed with; {}'.format(e))


class DataLiteralRep(DirectiveRep):
    def __repr__(self):
        return "<DataLit: {}>".format(self.attrs['content'])

    def size(self):
        raise NotImplementedError()

    def hexlify(self):
        content = self.attrs['content']

        if content.rstrip()[0:2] == '0x':
            return int(content, 16)
        elif content.rstrip()[0:2] == '0b':
            return int(content, 2)
        else:
            return content
