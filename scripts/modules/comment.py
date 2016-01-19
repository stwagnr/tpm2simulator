# -*- coding: utf-8 -*-

import textwrap as tw

from modules import constants


class Comment(object):
    """ Comment class:
    The class Comment wraps a string into a comment-compatible string. This
    means that a string is first splitted into lines of 'line_length'
    characters at maximum and that every line is prepended with a '// '
    sequence
    """

    indent = "// "
    table_subsequent_indent = "// " + 30 * " "
    line_length = 120

    # Initializes comment object
    def __init__(self):
        # initialize wrapper for simple text comments
        self.wrapper = tw.TextWrapper()
        self.wrapper.width = self.line_length
        self.wrapper.initial_indent = self.indent
        self.wrapper.subsequent_indent = self.indent

        # initialize wrapper for comments inside of xml tables
        self.table_wrapper = tw.TextWrapper()
        self.table_wrapper.width = self.line_length
        self.table_wrapper.initial_indent = self.indent
        self.table_wrapper.subsequent_indent = self.table_subsequent_indent

    # Performs simple comment wrapping of given string
    # Parameters:
    # str - string
    def wrap_comment(self, str):
        return self.wrapper.fill(str)

    # Generates comment from tables in xml format based on first two columns
    # Parameters:
    # table
    def extract_table(self, table):
        # Assuming that every table contains only two columns.

        comment = ""
        rows = table.find_all(constants.XML_TABLE_TABLE_ROW)

        # skip first row (table description)
        for i in range(1,len(rows)):
            unwrapped_comment = ""
            
            cells = rows[i].find_all(constants.XML_TABLE_TABLE_CELL)
            unwrapped_comment += '{:<29}'.format(cells[0].get_text()) # .encode("utf8")) 
            unwrapped_comment += cells[1].get_text() 
        
            comment += self.table_wrapper.fill(unwrapped_comment)
            comment += "\n"

        # comment += "\n"

        return comment

    # Generates comment from tables in text format based on first two columns
    # Parameters:
    # table
    def extract_table_pdf(self, table):
        # Assuming that every table contains only two columns.

        comment = "\n"

        # skip first row (table description)
        for i in range(1,len(table.rows)):
            unwrapped_comment = ""

            unwrapped_comment += '{:<29}'.format(table.rows[i][0])  # .encode("utf8"))
            unwrapped_comment += table.rows[i][1]

            comment += self.table_wrapper.fill(unwrapped_comment)
            comment += "\n"

        comment += "\n"

        return comment
