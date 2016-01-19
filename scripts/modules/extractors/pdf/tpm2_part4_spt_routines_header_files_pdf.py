# -*- coding: utf-8 -*-

from modules.extractors.pdf.tpm2_partx_extraction_navigator_pdf import ExtractionNavigator
from modules import data_structures
import re

class SptRoutinesHeaderFilesPDF(ExtractionNavigator):
    """
    """

    # Extract support routine headerfile code blocks
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # list of code blocks found in given part of file
    def extract_code_blocks(self, file, section_number, sub_section_number):
        code_blocks = data_structures.TPM2_Partx_File()

        code_offset = 0
        while True:
            line = file.readline()[:-1]
            if line == "":
                continue

            # end of page, either break, or calculate new offsets
            if "Page" in line and "Family" in line:
                for i in range(0, 5):
                    line = file.readline()[:-1]

                code_offset = 0

            result1 = re.search("^(\d{1,4})([^.].*)", line)
            if result1:
                line_number = result1.group(1)
                code_line = result1.group(2)
                code_offset = 4 - len(line_number) - 1

                s = code_line[code_offset:code_offset+1]

                if s is " ":
                    code_offset += 1

                code_line = code_line[code_offset:]
                code_blocks.append(data_structures.TPM2_Partx_CodeLine(code_line))

            else:
                if sub_section_number is not None and line.strip().startswith(str(section_number) + "." + str(sub_section_number+1)):
                    break
                elif sub_section_number is None and line.strip().startswith(section_number) or line.strip().startswith(str(int(section_number) + 1)):
                    break

        return code_blocks

    # Extract next function header from file
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # string containing function header
    # sub_section_number
    def next_function(self, file, section_number, sub_section_number):
        function = ""

        result = re.search("[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+([^ ]*?)\n", file)
        if result:
            function = result.group(1)
            file.seek(result.end())

        while not function.strip().endswith(".h"):
            sub_section_number += 1
            result = re.search("[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+([^ ]*?)\n", file)
            if result:
                function = result.group(1)
                file.seek(result.end())
            else:
                return None, None

        return function, sub_section_number

    # Append all function headers from file to the list of functions
    # Parameters;
    # file
    # section_number
    # sub_path
    def extract_function(self, file, section_number, sub_path):
        sub_section_number = 1
        function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find first function entry

        while function is not None:  # iterate over function entries

            if function == "BaseTypes.h":
                print "    * " + function.strip() + " SKIPPED"
                sub_section_number += 1
                function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find next function entry
                continue

            elif function == "Global.h":
                line = file.readline()[:-1]
                while "Includes" not in line.strip():
                    line = file.readline()[:-1]
                f = self.extract_code_blocks(file, section_number, sub_section_number)
            else:
                f = self.extract_code_blocks(file, section_number, None)

            print "    * " + function.strip()

            f.name = function.strip()
            f.short_name = f.name.replace(".h", "")
            f.file_name = f.name
            f.folder_name = sub_path

            self.functions.append(f)

            sub_section_number += 1

            function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find next function entry
