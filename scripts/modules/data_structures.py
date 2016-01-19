# -*- coding: utf-8 -*-

from modules.comment import Comment


# Internal representation of a code line from the specification
class TPM2_Partx_CodeLine:
    string = ""

    def __init__(self, string):
        self.string = ""
        self.string = string


# Internal representation of a comment line from the specification
class TPM2_Partx_CommentLine:
    string = ""

    def __init__(self, string):
        self.string = ""
        self.string = string


# Internal representation of a table from the specification
class TPM2_Partx_Table:
    name = ""
    short_name = ""
    number = 0
    rows = []
    table_type = None
    handles = []

    def __init__(self, name, short_name, number, rows):
        self.name = name
        self.short_name = short_name
        self.number = number
        self.rows = rows

    def append(self, row):
        self.rows.append(row)


# Internal representation of a file
class TPM2_Partx_File:
    name = ""
    short_name = ""
    folder_name = ""
    file_name = ""

    elements = []

    # only used if a command
    table_command = None
    table_response = None
    section_name = ""

    def __init__(self):
        self.name = ""
        self.short_name = ""
        self.file_name = ""
        self.folder_name = ""
        self.elements = []
        self.table_command = None
        self.table_response = None
        self.section_name = ""

    # Appends element to the list of elements if it is an instance of an internal data structure
    def append(self, element):
        if not (isinstance(element, TPM2_Partx_CodeLine) or isinstance(element, TPM2_Partx_CommentLine)
                or isinstance(element, TPM2_Partx_Table)):
            raise AssertionError()
        else:
            self.elements.append(element)

    # Converts list of elements into a string
    def elements_to_string(self):
        s = ""
        comment = Comment()
        for element in self.elements:
            # simple comment:
            if isinstance(element, TPM2_Partx_CommentLine) and element.string is not None:
                s += comment.wrap_comment(element.string) + "\n"
            # table comment:
            elif isinstance(element, TPM2_Partx_Table):
                s += comment.extract_table_pdf(element)
            elif isinstance(element, TPM2_Partx_CodeLine):
                s += element.string + '\n'
        return s

