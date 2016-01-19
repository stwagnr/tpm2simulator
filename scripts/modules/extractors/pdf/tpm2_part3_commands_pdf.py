# -*- coding: utf-8 -*-

import re  # regex

from modules.extractors.commands_extractor import CommandsExtractor
from modules.extractors.pdf.tpm2_partx_extraction_navigator_pdf import ExtractionNavigator
from modules import constants
from modules.extractors.table_extractor import TableExtractor
from modules import data_structures
from modules import utils


class CommandsExtractorPDF(CommandsExtractor, ExtractionNavigator):
    """
    """
    
    def __init__(self):
        CommandsExtractor.__init__(self)

    # Extract command code blocks
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # list of code blocks found in given file
    def extract_code_blocks(self, file, section_number):
        code_blocks = data_structures.TPM2_Partx_File()
        ###################################################################
        # FUNCTIONS BLOCKS (START)
        code_found = False
        table_found = False
        code_offset = 0
        while True:
            line = file.readline()[:-1]
            if line == "":
                continue

            # end of page, either break, or calculate new offsets
            if "Page" in line and "Family" in line:
                for i in range(0, 5):
                    line = file.readline()[:-1]

                if line.startswith(section_number) or line.startswith(str(int(section_number) + 1)):
                    break

            result1 = re.search("^(\d{1,4})(.*)", line)
            if result1:
                code_found = True
                table_found = False
                line_number = result1.group(1)
                code_line = result1.group(2)
                if code_offset == 0:
                    code_line = code_line.strip()
                    code_offset = line.find(code_line)
                else:
                    code_line = code_line[code_offset-len(line_number):]
                code_blocks.append(data_structures.TPM2_Partx_CodeLine(code_line))

            result2 = re.search("([ ]*Error Returns[ ]+Meaning.*)", line)
            if result2:
                table_found = True
                row = result2.group(1)+"\n"
                results = re.split("[ ]{5,}", row)
                offsets = []
                l = []
                for r in results:
                    r = r.strip()
                    l.append(r)
                    offsets.append(line.find(r))
                code_blocks.append(data_structures.TPM2_Partx_Table(None, None, None, l))
            elif table_found:
                row = line + "\n"
                row = utils.split_row(row, offsets)
                code_blocks.elements[len(code_blocks.elements)-1].append(row)

            result2 = re.search("^[ ]{2,}(.*)", line)
            if not (table_found or code_found) and result2:
                code_blocks.append(data_structures.TPM2_Partx_CommentLine(result2.group(1)))

            if not (result1 or result2):
                break
        # FUNCTIONS BLOCKS (END)
        ###################################################################

        return code_blocks

    # Append all functions from file to the list of functions
    # Parameters;
    # file
    # section_number
    # name_folder
    def extract_function(self, file, section_number, name_folder):
        sub_section_number = 1
        function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find first function entry

        while function is not None:  # iterate over function entries

            print " "*4 + "* " + function.strip()

            entry = self.next_entry(file, function, str(section_number) + "." + str(sub_section_number))
            file.seek(file.find(entry) + len(entry))
            
            f = self.extract_code_blocks(file, section_number)

            f.name = function.strip()
            f.short_name = f.name.replace(constants.TPM20_PREFIX_TPM2_, "")
            f.file_name = f.short_name + ".c"
            f.table_command = TableExtractor.extract_commands_table_command(file, f.short_name)
            f.table_response = TableExtractor.extract_commands_table_response(file, f.short_name)
            f.folder_name = name_folder

            self.functions.append(f)

            sub_section_number += 1
            function, sub_section_name = self.next_function(file, section_number, sub_section_number)  # find next function entry

    # Extract next command function from file
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # string containing function
    # sub_section_number
    def next_function(self, file, section_number, sub_section_number):

        function = ""
        result = re.search(section_number + "\." + str(sub_section_number) + "[ ]+([^.]*?)\n", file)
        if result:
            function = result.group(1)

        while (not (function.strip().startswith("_TPM_")
                        or function.strip().startswith("TPM2_"))):
            sub_section_number += 1
            result = re.search(section_number + "\." + str(sub_section_number) + "[ ]+([^.]*?)\n", file)
            if result:
                function = result.group(1)
            else:
                return None, None

        return function, sub_section_number

    # Get next entry from file
    # Parameters:
    # file
    # entry
    # section
    def next_entry(self, file, entry, section):
        result = re.search("(" + section + "\.\d+[ ]+Detailed Actions)\n", file)
        if result:
            entry = result.group(1)

        return entry
