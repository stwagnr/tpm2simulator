# -*- coding: utf-8 -*-

import re

from bs4 import Tag

from modules import utils
from modules import constants
from modules import data_structures
from modules.extractors.fodt.tpm2_partx_extraction_navigator_fodt import ExtractionNavigator


class SptRoutinesAnnexFODT(ExtractionNavigator):
    """
    """

    def __init__(self):
        ExtractionNavigator.__init__(self)

    # Extracts function
    # Parameters:
    # main_entry
    # name_section
    # sub_path
    def extract_function(self, main_entry, name_section, sub_path):
        # find first function entry
        function = self.next_function(main_entry, 2, True)

        # iterate over function entries
        while function is not None:

            print " "*4 + "* " + function.get_text().strip()

            if (function.get_text().strip() == "RSA Files"
                    or function.get_text().strip() == "Elliptic Curve Files"):
                backup = function
                while function is not None:
                    # find first function entry
                    function = self.next_function(function, 3)
                    if function is None:
                        break

                    print " "*8 + "- " + function.get_text().strip()

                    if function.get_text().strip() == "Alternative RSA Key Generation":
                        while True:
                            # find first function entry
                            function = self.next_function(function, 4, True)
                            if function is None:
                                break

                            print " "*12 + ". " + function.get_text().strip()
                            
                            self.handle_files(sub_path, function)
                    else:
                        self.handle_files(sub_path, function)

                function = backup
            else:
                self.handle_files(sub_path, function)

            # find next function entry
            function = self.next_function(function, 2)

    # Handles file
    # Parameters:
    # sub_path
    # function
    def handle_files(self, sub_path, function):
       
        # find the entry of the module to be extracted 
        entry = self.next_entry(function)

        # get all relevant code and comment blocks from the module
        f = self.extract_module(entry)

        f.name = function.get_text().strip()
        f.short_name = f.name.replace(".c", "")
        f.table_command = None
        f.table_response = None
        f.folder_name = sub_path

        self.functions.append(f)

    # Extract support routine annex code  blocks
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

    # Extracts module
    # Parameters:
    # entry
    def extract_module(self, entry):
        # find out which text:style-name of the list to follow
        style = self.extract_list_style(entry)

        code_blocks = self.extract_code_blocks(entry, style)

        return code_blocks 

    # Extracts list style
    # Parameters:
    # entry
    def extract_list_style(self, entry):
        style = None

        if (isinstance(entry, Tag)
                and entry.name == constants.XML_TEXT_LIST
                and entry.has_attr(constants.XML_TEXT_STYLE_NAME)):
            style = entry[constants.XML_TEXT_STYLE_NAME]
        elif (isinstance(entry, Tag)
                and entry.name == constants.XML_TEXT_P):
            """ propagate confusion:
            we need two next_sibling invocations to access the next sibling
            """

            next_list = entry.next_sibling.next_sibling
            while (isinstance(next_list, Tag) 
                    and next_list.name == constants.XML_TEXT_LIST):
                # comment found: need to find the list with code entries
                tp = next_list.find(constants.XML_TEXT_P)
                if tp is not None:
                     ts = tp.find(constants.XML_TEXT_SPAN)
                     if (ts is not None
                            and ts.has_attr(constants.XML_TEXT_STYLE_NAME)
                            and ts[constants.XML_TEXT_STYLE_NAME].startswith(constants.XML_PREFIX_CODE_)):
                        style = next_list[constants.XML_TEXT_STYLE_NAME]
                        break
                next_list = next_list.find_next(constants.XML_TEXT_LIST)

        return style

    # Extract next function from annex
    # Parameters;
    # cur_function
    # num
    # first_intro
    # Returns:
    # string containing next function from annex
    # sub_section_number
    def next_function(self, cur_function, num, first_intro=False):
        function = cur_function.find_next(constants.XML_TEXT_H)
        while (isinstance(function, Tag)
               and function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
               and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) != num
               or (first_intro and function.get_text().strip() == "Introduction")
               or function.get_text().strip().endswith("Format")):
            function = function.find_next(constants.XML_TEXT_H)
            if function is None \
                    or (function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
                        and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) < num):
                return None

        if function.get_text().strip() == "Introduction":
            return None

        return function

    # Extracts next entry
    # Parameters:
    # entry
    def next_entry(self, entry):
        while True: # do-while
            entry = entry.find_next(ExtractionNavigator.selector)
            if entry is not None:
                text_p = entry.find(constants.XML_TEXT_P)
                if text_p is not None:
                    found = False
                    text_span = text_p.find_all(constants.XML_TEXT_SPAN)
                    for ts in text_span:
                        if (ts is not None 
                                and ts.has_attr(constants.XML_TEXT_STYLE_NAME)
                                and ts[constants.XML_TEXT_STYLE_NAME].startswith(constants.XML_PREFIX_CODE_)):
                            found = True
                            break
                    if found:
                        break

        return entry

    # Extracts section
    # Parameters:
    # entry
    # name_section
    # name_folder
    def extract_section(self, entry, name_section, name_folder):
        """
        The method 'extract_section' is overwritten since this class looks for
        the 'annex' part of the supporting routines, which is indicated by the
        list's text:style-name 'WWNum2' instead of the general search criterion
        'XML_TEXT_H' and 'constants.XML_TEXT_OUTLINE_LEVEL: 1'.
        """

        cur_name = ""
        
        # find correct section
        while isinstance(entry, Tag) and cur_name != name_section:
            entry = entry.find_next(constants.XML_TEXT_LIST,
                    {constants.XML_TEXT_STYLE_NAME: 'WWNum2'})
            text_p = entry.find(constants.XML_TEXT_P)
            if text_p is not None:
                cur_name = text_p.get_text().strip()

        # couldn't find the right section
        if entry is None:
            return

        print("[+] Section name: {0}".format(entry.find(constants.XML_TEXT_P).get_text().strip()))

        self.extract_function(entry, name_section, name_folder)