import os
class DuplicateLabelError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'Two instances of the label "'+self.value+'" were found'

class FileNonExistantError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'The file "'+self.value+'" cannot be found in the directory '+os.getcwd()

class FileExistsError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'The file "'+self.value+'" already exists, and the user chose not to overwrite it'
