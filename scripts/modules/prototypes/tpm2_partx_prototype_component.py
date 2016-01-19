# -*- coding: utf-8 -*-


class PrototypeComponent:

    def __init__(self):
        self.content = u''

    # Appends string to the string of contents
    # Parameters:
    # content - string to be added
    def append(self, content):
        self.content += content