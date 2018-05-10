import codecs

class RotEncoder:
    def __init__(self):
        self.rot13 = codecs.getencoder('rot13')

    def encode_string(self, string):
        return self.rot13(string)[0]