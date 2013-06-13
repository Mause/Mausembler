import os
import re
import logging

from .definitions import basic_opcodes, values, special_opcodes


class ReferenceRep(object):
    pass


# class Expression(object):
#     def __init__(self, expr):
#         self.HEX_RE = re.compile(r'(0x\d+)')
#         self.BIN_RE = re.compile(r'(0b[01]+)')

#     def resolve(self):
#         return 'new_assembly'


class Rep(object):
    def __init__(self, assembler_ref, **kwargs):
        self.assembler_ref = assembler_ref
        self.attrs = kwargs

    def size(self):
        raise NotImplementedError(self.__class__)

    def hexlify(self, state):
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

    def hexlify(self, state):
        return None


class LabelRep(Rep):
    def size(self):
        return 0

    def __repr__(self):
        return "<Label: {}>".format(self.attrs['name'])


class OpcodeRep(Rep):
    REF_RE = re.compile(r'\[(?P<ref_content>.*)\]')
    LITERAL_RE = re.compile(r'(?:0x|0b)?\d+')
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

    def assemble_opcode(self):
        "Does the actual parsing and assembling"

        # hex( (0x1f << 10) ^ (0x0 << 4) ^ 0x1 )
        # returns 0x7c01
        # sample code as supplied by startling

        # hex(0x7c<<24 ^ 0x2<<20 ^ 0x1<<16 ^ 0x1)
        # returns 0x7c11f888
        # my own (revised) reference code

        assert (
            self.attrs['name'] in basic_opcodes or
            self.attrs['name'] in special_opcodes
        )

        opcode_frag_a = self.attrs['frag_a']

        if isinstance(self, BasicOpcodeRep):
            # In bits (in LSB-0 format), a basic instruction has the format:
                # aaaaaabbbbbooooo
            # will take the next word literally, unless otherwise specified
            opcode_val = basic_opcodes[self.attrs['name']]

            # print(self.attrs, list(map(type, self.attrs)))

            # self.debug('perform {} operation with {} and {}'.format(
            #     self.attrs['name'],
            #     hex(self.attrs['frag_b']),
            #     hex(self.attrs['frag_a'])))

            opcode_frag_b = self.attrs['frag_b']

            final = self._assemble_opcode(
                opcode_val,
                opcode_frag_a,
                opcode_frag_b)

        elif isinstance(self, SpecialOpcodeRep):
            # Special opcodes always have their lower five bits unset,
            # have one value and a five bit opcode.
            # In binary, they have the format: aaaaaaooooo00000
            opcode_val = special_opcodes[self.attrs['name']]

            self.debug('perform {} operation with {}'.format(
                self.attrs['name'],
                hex(self.attrs['frag_a'])))

            final = self._assemble_opcode(
                opcode_val,
                opcode_frag_a)
        else:
            raise Exception(self)

        # print('final:', hex(final))

        return final

    def _assemble_opcode(self, opcode_val, opcode_frag_a, opcode_frag_b=None):
        output_data = [0x1f, opcode_val]
        if opcode_frag_b:
            output_data += [opcode_frag_b, opcode_frag_a]
        else:
            output_data += [opcode_frag_a]

        # output_data[0] = int(output_data[0]) << 26
        # # output_data[1] = int(output_data[1]) << 18
        # output_data[1] = int(output_data[1]) << 16
        # output_data[2] = int(output_data[2]) << 16

        # final = (output_data[0] ^ output_data[1])
        # final = (final ^ output_data[2])

        final = (
            int(output_data[0]) << 26 ^
            int(output_data[1]) << 16 ^
            int(output_data[2]) << 16)

        if opcode_frag_b:
            final = (final ^ output_data[3])

        return final

    def resolve_expressions(self):
        if 'frag_a' in self.attrs:
            self.attrs['frag_a'] = self.resolve_single_expression(self.attrs['frag_a'])
            assert self.attrs['frag_a'] is not None

        if 'frag_b' in self.attrs:
            self.attrs['frag_b'] = self.resolve_single_expression(self.attrs['frag_b'])
            assert self.attrs['frag_b'] is not None

    def resolve_single_expression(self, expression):
        # try and resolve it normally
        expression = self.resolve_frag(expression)
        if type(expression) == int:
            # assert expression, 'bad returned frag'
            return expression

        if not self.LITERAL_RE.match(expression):
            # print('not literal:', expression)

            match = self.REF_RE.match(expression)
            if match:
                print('is reference:', match.groups())

            else:
                # print('is label:', expression)
                expression = self.resolve_label(expression)
                assert expression

        return expression

    def resolve_label(self, label_name):
        if label_name not in self.assembler_ref.labels:
            raise Exception('No such label: {}'.format(label_name))

        if self.assembler_ref.labels[label_name] is not None:
            return self.assembler_ref.labels[label_name]
        else:
            # this is where we determine the address for the label
            address = 0x0
            for opcode in self.state['assembly']:
                if isinstance(opcode, LabelRep):
                    if opcode.attrs['name'] == label_name:
                        break
                else:
                    address += opcode.size()
            else:
                raise Exception('label not found?! wut?!')

            self.assembler_ref.labels[label_name] = address

        return address


class BasicOpcodeRep(OpcodeRep):
    def __repr__(self):
        return "<BasicOpcode: {} {} {}>".format(
            self.attrs['name'],
            self.attrs['frag_b'],
            self.attrs['frag_a'])

    def hexlify(self, state):
        self.state = state
        # TODO: add code here to resolve label references

        self.resolve_expressions()

        h = self.assemble_opcode()
        assert h, h

        del self.state
        return h

    def size(self):
        return 2

    def resolve(self, state):
        pass


class SpecialOpcodeRep(OpcodeRep):
    def __repr__(self):
        return "<SpecialOpcode: {} {}>".format(
            self.attrs['name'],
            self.attrs['frag_a'])

    def hexlify(self, state):
        # TODO: add code here to resolve label references

        self.resolve_expressions()

        h = self.assemble_opcode(self)
        assert h, h
        return h


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

    def hexlify(self, state):
        content = self.attrs['content']

        if content.rstrip()[0:2] == '0x':
            return int(content, 16)
        elif content.rstrip()[0:2] == '0b':
            return int(content, 2)
        else:
            return content
