

class AssemblerException(Exception):
    pass


class DuplicateLabelError(AssemblerException):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return 'Two instances of the label "{}" were found in the file {}\n* {}\n* {}'.format(
            self.value[0],
            self.value[1],
            self.value[2][self.value[0]],
            self.value[3])


class DASMSyntaxError(AssemblerException):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '"{}" was not recognised as valid assembly'.format(self.value)


class ReservedKeyword(AssemblerException):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return '"{}" is a reserved keyword'.format(self.value)
