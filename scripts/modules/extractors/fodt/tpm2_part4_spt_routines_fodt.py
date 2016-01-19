# -*- coding: utf-8 -*-

import re

from bs4 import Tag

from modules import utils
from modules.extractors.fodt.tpm2_partx_extraction_navigator_fodt import ExtractionNavigator
from modules import constants
from modules import data_structures


class SptRoutinesFODT(ExtractionNavigator):
    """
    """

    def __init__(self):
        ExtractionNavigator.__init__(self)

    # Extract support routine code blocks
    # Parameters;
    # entry
    # style
    # Returns:
    # list of code blocks found in given part of file
    def extract_code_blocks(self, entry, style):

        code_blocks = data_structures.TPM2_Partx_File()

        style_nr = int(re.search("([0-9]+)", style).group(1))

        cont = ExtractionNavigator.selector(entry)
        while cont:

            # if the current entry is a text:p, table:table, or test:list with the current style,
            # append it to code blocks
            if isinstance(entry, Tag) and entry.name == constants.XML_TEXT_P:
                element = data_structures.TPM2_Partx_CommentLine(entry.get_text())
                code_blocks.append(element)  # once
            elif isinstance(entry, Tag) and entry.name == constants.XML_TABLE_TABLE:
                table_rows = []
                rows = entry.find_all(constants.XML_TABLE_TABLE_ROW)
                for i in range(0,len(rows)):
                    r = []
                    cells = rows[i].find_all(constants.XML_TABLE_TABLE_CELL)
                    for cell in cells:
                        r.append(cell.get_text())
                    table_rows.append(r)
                element = data_structures.TPM2_Partx_Table("","", 0, table_rows)
                code_blocks.append(element)  # once
            elif isinstance(entry, Tag) and entry.name == constants.XML_TEXT_LIST\
                    and entry.has_attr(constants.XML_TEXT_STYLE_NAME) \
                    and entry[constants.XML_TEXT_STYLE_NAME] == style:
                text_ps = entry.findAll(constants.XML_TEXT_P)

                for text_p in text_ps:
                    if not isinstance(text_p, Tag):
                        break
                    utils.convert_indentation(text_p)
                    text_p_text = text_p.get_text()
                    element = data_structures.TPM2_Partx_CodeLine(text_p_text)
                    code_blocks.append(element)  # for every code line

                # add an empty line for readability
                element = data_structures.TPM2_Partx_CodeLine("")
                code_blocks.append(element)  # once

            next_list = entry
            current_style_nr = style_nr
            cont = False
            while current_style_nr - style_nr < 2 or current_style_nr - style_nr > 4:
                if next_list:
                    next_list = next_list.next_sibling.next_sibling
                else:
                    break
                if next_list and next_list.has_attr(constants.XML_TEXT_STYLE_NAME):
                    current_style = next_list[constants.XML_TEXT_STYLE_NAME]
                    result = re.search("WWNum([0-9]+)", current_style)
                    if result and int(result.group(1)) > style_nr:
                        current_style_nr = int(result.group(1))
                    if current_style == style:
                        cont = True
                        break

            entry = entry.next_sibling.next_sibling

        return code_blocks

    # Append all functions from file to the list of functions
    # Parameters;
    # main_entry
    # name_section
    # name_folder
    def extract_function(self, main_entry, name_section, name_folder):
        function = self.next_function(main_entry)

        while function is not None:

            if isinstance(function, Tag) and "Implementation.h" in function.get_text():
                break

            print "    * " + function.get_text().strip()

            # Skip Marshal.c (this file is created separately)
            if function.get_text().strip() == "Marshal.c":
                function = self.next_function(function)
                continue

            entry = self.next_entry(function)

            style = None

            # find style of code block
            if (isinstance(entry, Tag)
                and entry.name == constants.XML_TEXT_LIST
                and entry.has_attr(constants.XML_TEXT_STYLE_NAME)):
                style = entry[constants.XML_TEXT_STYLE_NAME]
                style_nr = int(re.search("([0-9]+)", style).group(1))

            f = self.extract_code_blocks(entry, style)

            f.name = self.correct_name(function)
            f.short_name = f.name.replace(".c", "")
            f.file_name = f.name.replace("()", ".c")
            f.table_command = None
            f.table_response = None
            f.folder_name = name_folder

            self.functions.append(f)

            # find next function
            function = self.next_function(function)

    # Change the name of the function to the correct one
    # Parameters:
    # function
    # Returns:
    # name - correct name
    @staticmethod
    def correct_name(function):
        name = function.get_text().strip()
        if "ParseHandleBuffer()" in name:
            name = "HandleProcess_fp.h"
        elif name.endswith("()"):
            name = name.replace("()", "_fp.h")
        elif name.endswith(")"):
            name = utils.find_tpm_base_type_name(name)

        return name

    # Extract next function from file
    # Parameters;
    # entry
    # Returns:
    # string containing function\
    def next_function(self, entry):
        function = entry.find_next(constants.XML_TEXT_H)
        while (isinstance(function, Tag)
               and ((function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
                     and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) != 2)
                    # supporting routines:
                    or function.get_text().strip() == "Introduction")):
            function = function.find_next(constants.XML_TEXT_H)

            if (function is not None
                and function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
                and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) < 2):
                return None

        return function

    # Get next entry
    # Parameters:
    # entry - xml file pointing to current entry
    # Returns:
    # entry - same xml file pointing to next entry
    def next_entry(self, entry):
        while True:  # do-while
            entry = entry.find_next(ExtractionNavigator.selector)  # constants.XML_TEXT_LIST)

            if entry is not None:
                """
                NOTE: not yet sure whether the (uncommented) check for 'text:p' is needed here
                      -> this would be needed if we would like to include comments in
                         Introduction sections and similar...
                      -> this means: at the moment, we do not support code that starts with a comment
                         (before includes in the code)
                      -> same applies not only for 'simple comments' but for 'table-comments' as well
                """

                if entry.name == constants.XML_TEXT_LIST:
                    text_p = entry.find(constants.XML_TEXT_P)
                    if text_p is not None:
                        text_span = text_p.find(constants.XML_TEXT_SPAN)
                        if (text_span is not None
                            and text_span.has_attr(constants.XML_TEXT_STYLE_NAME)
                            and text_span[constants.XML_TEXT_STYLE_NAME].startswith(
                                constants.XML_PREFIX_CODE_)):
                            break

        return entry

