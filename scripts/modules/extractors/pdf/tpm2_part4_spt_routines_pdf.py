# -*- coding: utf-8 -*-

import re
from modules import data_structures
from modules import utils
from modules.extractors.pdf.tpm2_partx_extraction_navigator_pdf import ExtractionNavigator
import settings

class SptRoutinesPDF(ExtractionNavigator):

    def handle_cryptographic_functions(self, file, sub_path, section_number, sub_section_number):

        function = ""
        sub_sub_section_number = 0

        while not (section_number + "\." + str(sub_section_number + 1) in function and (function.strip().endswith(".c") or function.strip().endswith(".h"))):
            sub_sub_section_number += 1
            regex = "\n[ ]*" + section_number + "\." + str(sub_section_number) + "\." + str(sub_sub_section_number) + "[ ]*(.*\.c|.*\.h)"
            result = re.search(regex, file)
            if result:
                function = result.group(1)
                print "        * " + function.strip()
            else:
                break

	    f = self.extract_code_blocks_cryptographic_functions(file, section_number, sub_section_number, sub_sub_section_number)

	    f.name = function.strip()
	    f.short_name = f.name[:-2]
	    f.file_name = f.name.replace("()", ".c")
	    f.folder_name = sub_path

	    self.functions.append(f)

    # Extract support routine code blocks
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # list of code blocks found in given part of file
    def extract_code_blocks(self, file, section_number, sub_section_number):
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
                    if re.search("Part[ ]+4:", line):
                        code_offset = len(re.search("\f([ ]*).*", line).group(1))

                if "Annex" in line:
                    return code_blocks

                if line.strip().startswith(section_number + "." + str(int(sub_section_number) +1)):
                    break

                if (line.startswith("  ") and str(int(section_number) + 1) + "    " in line.strip()
                        and not section_number + "." + str(sub_section_number) in line):
                    file.seek(file.tell() - len(line))
                    break

            result1 = re.search("^(\d{1,4}[ ]*)(.*)", line)
            if result1:
                code_found = True
                table_found = False
                if code_offset == 0:
                    code_offset = len(result1.group(1))
                code_line = line[code_offset:]
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
            elif line.strip().startswith(section_number + "." + str(int(sub_section_number) +1)):
                break

            result2 = re.search("^[ ]{2,}(.*)", line)
            if not (table_found or code_found) and result2:
                code_blocks.append(data_structures.TPM2_Partx_CommentLine(result2.group(1)))

            if not (result1 or result2):
                break
        # FUNCTIONS BLOCKS (END)
        ###################################################################

        return code_blocks

    # Extract next function from file
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # string containing function
    # sub_section_number
    def next_function(self, file, section_number, sub_section_number):
        function = ""

        if settings.SPEC_VERSION_INT == 138:
                result = re.search("\n[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+(.*?[^.\d]{2,})\n", file)
        else:
                result = re.search("\n[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+(.*?[^.\d]{2,}(.c|.h|\(.*?\)))\n", file)
        if result:
            function = result.group(1)
            file.seek(result.end())

        while not (function.strip().endswith(".c") or function.strip().endswith(")") or "Headers" in function or "Source" in function):

            sub_section_number += 1

            if settings.SPEC_VERSION_INT == 138:
                result = re.search("\n[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+(.*?[^.\d]{2,})\n", file)
            else:
                result = re.search("\n[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+(.*?[^.\d]{2,}(.c|.h|\(.*?\)))\n", file)
            if result:
                function = result.group(1)
                file.seek(result.end())
            else:
                return None, None

        return function, sub_section_number

    # Append all functions from file to the list of functions
    # Parameters;
    # file
    # section_number
    # sub_path
    def extract_function(self, file, section_number, sub_path):
        sub_section_number = 1
        function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find first function entry

        while function is not None:  # iterate over function entries

            print "    * " + function.strip()

	    if section_number == "10" and ("Headers" in function or "Source" in function):
		self.handle_cryptographic_functions(file, sub_path, section_number, sub_section_number)
		sub_section_number += 1
                function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find next function entry
		continue

            f = self.extract_code_blocks(file, section_number, sub_section_number)

            if "CommandDispatcher()" in function:
                f.file_name = "CommandDispatcher_fp.h"
                f.name = "CommandDispatcher_fp.h"
                f.short_name = "CommandDispatcher"
                f.folder_name = sub_path
            elif "ParseHandleBuffer()" in function:
                f.file_name = "HandleProcess_fp.h"
                f.name = "HandleProcess_fp.h"
                f.short_name = "HandleProcess"
                f.folder_name = sub_path
            elif "Marshal.c" in function:
                sub_section_number += 1
                function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find next function entry
                continue
            else:

                result = re.search(".*?\((.*?)\)", function)
                if result:
                    f.file_name = result.group(1)
                    f.name = result.group(1)
                else:
                    f.file_name = function.strip().replace("()", ".c")
                    f.name = function.strip()

                f.short_name = f.name[:-2]
                f.folder_name = sub_path

            self.functions.append(f)

            sub_section_number += 1

            function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find next function entry

    # Extract support routine annex code  blocks
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # list of code blocks found in given part of file
    def extract_code_blocks_cryptographic_functions(self, file, section_number, sub_section_number, sub_sub_section_number=None):
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
                    line = file.readline()
                    if "Part 4: Supporting Routines" in line:
                        result1 = re.search("([ ]+)(.*)\n", line)
                        if result1:
                            code_offset = len(result1.group(1))

                if line.strip().startswith(section_number + "." + str(int(sub_section_number) +1)):
                    file.seek(file.tell() - len(line))
                    break

                if sub_sub_section_number and line.strip().startswith(section_number + "." + str(sub_section_number) + "." + str(int(sub_sub_section_number) +1)):
                    break

            result1 = re.search("^(\d{1,4})(.*)", line)
            if result1:
                code_found = True
                table_found = False
                line_number = result1.group(1)
                code_line = result1.group(2)
                if code_offset == 0:
                    code_line = code_line.strip()
                    code_offset = max(line.find(code_line), len(line_number) + 2)
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
            elif line.strip().startswith(section_number + "." + str(int(sub_section_number) +1)):
                break
            elif sub_sub_section_number and line.strip().startswith(section_number + "." + str(sub_section_number) + "." + str(int(sub_sub_section_number) + 1)):
                break

            result2 = re.search("^[ ]{2,}(.*)", line)
            if not (table_found or code_found) and result2:
		code_blocks.append(data_structures.TPM2_Partx_CommentLine(""))
                code_blocks.append(data_structures.TPM2_Partx_CommentLine(result2.group(1)))

	    # reset code status for comments
	    code_found = False

            if not (result1 or result2):
                break
        # FUNCTIONS BLOCKS (END)
        ###################################################################

        return code_blocks
