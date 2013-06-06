import os
import re


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
    pass


class BasicOpcodeRep(OpcodeRep):
    contains_reference = False

    def __repr__(self):
        return "<BasicOpcope: {} {} {}>".format(
            self.attrs['name'],
            self.attrs['frag_b'],
            self.attrs['frag_a'])

    def hexlify(self):
        # TODO: add code here to resolve label references

        assert not self.contains_reference
        return self.assembler_ref.assemble_opcode(self)

    def resolve(self, state):
        # add code to expand arithmetic here
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
