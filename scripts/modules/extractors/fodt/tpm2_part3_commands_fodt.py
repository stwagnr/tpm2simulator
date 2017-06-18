# -*- coding: utf-8 -*-

from bs4 import Tag

from modules.extractors.fodt.tpm2_partx_extraction_navigator_fodt import ExtractionNavigator
from modules.extractors.commands_extractor import CommandsExtractor
from modules.extractors.table_extractor import TableExtractor
from modules import utils, constants
from modules import data_structures


class CommandsExtractorFODT(CommandsExtractor, ExtractionNavigator):
    """
    """
    
    def __init__(self):
        CommandsExtractor.__init__(self)

    # Extracts command function from part 3 of specification
    # Parameters:
    # function
    # style
    def extract_tpm2_part3_command(self, function, style):
        command = data_structures.TPM2_Partx_File()

        entry = self.next_entry(function)

        """ distinguish between a text:list and a text:p tag:
        In case the tag is of type: text:list simply use its text:style-name as
        condition for further iteration (to find futher lines of the code).
        In case the tag is of type text:p, use its siblings text:style-name --
        assuming its next_sibling is of type text:list.
        """

        # extract the style
        if entry.name == constants.XML_TEXT_LIST:
            style = entry[constants.XML_TEXT_STYLE_NAME]
        if entry.name == constants.XML_TEXT_P:
            style = entry.next_sibling.next_sibling[constants.XML_TEXT_STYLE_NAME]

        # entry tag is of type text:list, text:p or table:table
        continue_extraction = self.selector(entry)

        while continue_extraction:
            if entry.name == constants.XML_TEXT_P:
                element = data_structures.TPM2_Partx_CommentLine(entry.get_text())
                command.append(element)  # once
            elif entry.name == constants.XML_TABLE_TABLE:
                table_rows = []
                rows = entry.find_all(constants.XML_TABLE_TABLE_ROW)
                for i in range(0,len(rows)):
                    r = []
                    cells = rows[i].find_all(constants.XML_TABLE_TABLE_CELL)
                    for cell in cells:
                        r.append(cell.get_text())
                    table_rows.append(r)
                element = data_structures.TPM2_Partx_Table("","", 0, table_rows)
                command.append(element)  # once
            elif entry.name == constants.XML_TEXT_LIST:
                text_ps = entry.findAll(constants.XML_TEXT_P)

                for text_p in text_ps:
                    if not isinstance(text_p, Tag):
                        break
                    utils.convert_indentation(text_p)
                    text_p_text = text_p.get_text()
                    element = data_structures.TPM2_Partx_CodeLine(text_p_text)
                    command.append(element)  # for every code line

                command.append(data_structures.TPM2_Partx_CodeLine(""))

            entry = entry.find_next(self.selector)

            if not isinstance(entry, Tag):
                continue_extraction = False
                continue

            if entry.name == constants.XML_TEXT_P:
                continue_extraction = True
            elif entry.name == constants.XML_TEXT_LIST:
                continue_extraction = (entry[constants.XML_TEXT_STYLE_NAME] == style)
            elif entry.name == constants.XML_TABLE_TABLE:
                next_list = entry.find_next(constants.XML_TEXT_LIST)
                continue_extraction = (next_list[constants.XML_TEXT_STYLE_NAME] == style)
            else:
                continue_extraction = False

        return command

    # Append all functions from file to the list of functions
    # Parameters;
    # main_entry
    # name_section
    # name_folder
    def extract_function(self, main_entry, name_section, name_folder):
        function = self.next_function(main_entry)  # find first function entry

        while function is not None:  # iterate over function entries

            print " "*4 + "* " + function.get_text().strip()

            f = self.extract_tpm2_part3_command(function, None)

            f.name = function.get_text()
            f.short_name = f.name.replace(constants.TPM20_PREFIX_TPM2_, "")
            f.file_name = f.short_name + ".c"
            f.table_command = TableExtractor.extract_commands_table_command(function, f.short_name)
            f.table_response = TableExtractor.extract_commands_table_response(function, f.short_name)
            f.folder_name = name_folder
            f.section_name = name_section

            self.functions.append(f)
            function = self.next_function(function)  # find next function entry

    # Extract next command function from file
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # xml tag containing function
    def next_function(self, entry):
        function = entry.find_next(constants.XML_TEXT_H)
        while (isinstance(function, Tag)
               and function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
               and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) >= 2
               and not (function.get_text().strip().startswith("_TPM_")
                        or function.get_text().strip().startswith("TPM2_"))):
            function = function.find_next(constants.XML_TEXT_H)

        if (function is None
            or (function.has_attr(constants.XML_TEXT_OUTLINE_LEVEL)
                and int(function[constants.XML_TEXT_OUTLINE_LEVEL]) != 2)):
            return None

        return function

    # Get next entry from xml file
    # Parameters:
    # entry
    def next_entry(self, entry):
        entry = entry.find_next(constants.XML_TEXT_H, {constants.XML_TEXT_OUTLINE_LEVEL: '3'})
        while isinstance(entry, Tag) and entry.get_text().strip() != "Detailed Actions":
            entry = entry.find_next(text='Detailed Actions').parent

        # print entry.get_text().strip()
        section_entry = entry

        # find next valid tag representing the first line of code or an outlined comment
        entry = section_entry.find_next(self.selector)

        return entry


