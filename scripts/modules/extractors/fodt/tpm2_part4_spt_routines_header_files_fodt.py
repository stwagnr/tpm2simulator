# -*- coding: utf-8 -*-

import re

from bs4 import Tag

from modules.extractors.fodt.tpm2_partx_extraction_navigator_fodt import ExtractionNavigator
from modules import utils, constants
from modules import data_structures


class SptRoutinesHeaderFilesFODT(ExtractionNavigator):
    """
    """

    # Extracts next entry
    # Parameters
    # cur_function
    def next_entry(self, cur_function):
        function = cur_function.find_next(constants.XML_TEXT_H)
        while (isinstance(function, Tag)
               and function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
               and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) >= 2
               and not (function.get_text().strip().endswith(".h") or function.get_text().strip().endswith(".c"))):
            function = function.find_next(constants.XML_TEXT_H)

        if function is None:
            return None

        if function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL) and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) != 2:
            return None

        return function

    # Extract support routine headerfile code blocks
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

    # Append all function headers from file to the list of functions
    # Parameters;
    # main_entry
    # name_section
    # sub_path
    def extract_function(self, main_entry, name_section, sub_path):
        function = self.next_entry(main_entry)  # find first function entry

        while function is not None:  # iterate over function entries

            if function.get_text() == "BaseTypes.h":
                print "    * " + function.get_text().strip() + " SKIPPED"
                function = self.next_entry(function)  # find next function entry
                continue

            print "    * " + function.get_text().strip()

            entry = function.find_next(constants.XML_TEXT_LIST)
            while not entry.has_attr(constants.XML_TEXT_STYLE_NAME):
                entry = entry.find_next(constants.XML_TEXT_LIST)

            if function.get_text() == "Global.h":
                entry = function.find_next(constants.XML_TEXT_H, {constants.XML_TEXT_OUTLINE_LEVEL: '3'})
                while isinstance(entry, Tag) and entry.get_text().strip() != "Includes":
                    entry = entry.find_next(constants.XML_TEXT_H, {constants.XML_TEXT_OUTLINE_LEVEL: '3'})
                entry = entry.find_next(constants.XML_TEXT_LIST)

            style = entry[constants.XML_TEXT_STYLE_NAME]

            f = self.extract_code_blocks(entry, style)

            f.name = function.get_text()
            f.short_name = f.name.replace(".h", "")
            f.table_command = None
            f.table_response = None
            f.folder_name = sub_path

            self.functions.append(f)

            function = self.next_entry(function)  # find next function entry
