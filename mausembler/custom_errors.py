class DuplicateLabelError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return 'Two instances of the label "'+self.value+'" were found'
    #   return repr(self.value)