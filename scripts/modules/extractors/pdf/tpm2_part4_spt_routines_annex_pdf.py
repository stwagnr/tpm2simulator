# -*- coding: utf-8 -*-

import re
from modules.extractors.pdf.tpm2_partx_extraction_navigator_pdf import ExtractionNavigator
from modules import data_structures
from modules import utils


class SptRoutinesAnnexPDF(ExtractionNavigator):

    # Handle RSA ECC
    # Parameters:
    # file
    # sub_path
    # section_number
    # sub_section_number
    def handle_RSA_ECC(self, file, sub_path, section_number, sub_section_number):
        function = ""
        sub_sub_section_number = 0

        while not (section_number + "\." + str(sub_section_number + 1) in function and (function.strip().endswith(".c") or function.strip().endswith(".h"))):
            sub_sub_section_number += 1
            regex = "\n[ ]*" + section_number + "\." + str(sub_section_number) + "\." + str(sub_sub_section_number) + "\.[ ]+([^.\d]*?(\.c|\.h|\n))"
            result = re.search(regex, file)
            if result:
                function = result.group(1)
            else:
                break

            if function.strip() == "Alternative RSA Key Generation":
                print " "*8 + ". " + function.strip()
                sub_sub_sub_section_number = 2  # skip introduction
                while True:
                    # find first function entry
                    regex = "\n[ ]*" + section_number + "\." + str(sub_section_number) + "\." + str(sub_sub_section_number) + "\." + str(sub_sub_sub_section_number) + ".[ ]+([^.\d]*?(\.c|\.h|\n))"
                    result = re.search(regex, file)
                    if result:
                        function = result.group(1)
                    else:
                        return

                    print " "*12 + ". " + function.strip()

                    f = self.extract_code_blocks(file, section_number, sub_section_number, sub_sub_section_number, sub_sub_sub_section_number)
                    f.name = function.strip()
                    f.short_name = f.name[:-2]
                    f.file_name = f.name.replace("()", ".c")
                    f.folder_name = sub_path

                    self.functions.append(f)

                    sub_sub_sub_section_number += 1
            else:
                f = self.extract_code_blocks(file, section_number, sub_section_number, sub_sub_section_number)

                print " "*8 + ". " + function.strip()

                f.name = function.strip()
                f.short_name = f.name[:-2]
                f.file_name = f.name.replace("()", ".c")
                f.folder_name = sub_path

                self.functions.append(f)

    # Extract support routine annex code  blocks
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # list of code blocks found in given part of file
    def extract_code_blocks(self, file, section_number, sub_section_number, sub_sub_section_number=None, sub_sub_sub_section_number=None):
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

                s = "Annex " + str(chr(ord(section_number) + 1))
                if line.strip().startswith(section_number + "." + str(int(sub_section_number) +1)) \
                        or (s in line):
                    file.seek(file.tell() - len(line))
                    break

                if sub_sub_section_number and line.strip().startswith(section_number + "." + str(sub_section_number) + "." + str(int(sub_sub_section_number) +1)):
                    break

                if sub_sub_section_number and sub_sub_sub_section_number \
                        and line.strip().startswith(section_number + "." + str(sub_section_number) + "." + str(sub_sub_section_number) + "." + str(int(sub_sub_sub_section_number) +1)):
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
            if sub_sub_section_number and sub_sub_sub_section_number \
                    and line.strip().startswith(section_number + "." + str(sub_section_number) + "." + str(sub_sub_section_number) + "." + str(int(sub_sub_sub_section_number) +1)):
                break

            result2 = re.search("^[ ]{2,}(.*)", line)
            if not (table_found or code_found) and result2:
                code_blocks.append(data_structures.TPM2_Partx_CommentLine(result2.group(1)))

            if not (result1 or result2):
                break
        # FUNCTIONS BLOCKS (END)
        ###################################################################

        return code_blocks

    # Extract next function from annex
    # Parameters;
    # file
    # section_number
    # sub_section_number
    # Returns:
    # string containing next function from annex
    # sub_section_number
    def next_function(self, file, section_number, sub_section_number):
        function = ""

        result = re.search("\n[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+(.*?[^.\d]{2,})\n", file)
        if result:
            function = result.group(1)
            file.seek(result.end())

        while not (function.strip().endswith(".c") or function.strip().endswith(".h") or "RSA Files" in function or "Elliptic Curve Files" in function):
            sub_section_number += 1
            result = re.search("\n[ ]*" + section_number + "\." + str(sub_section_number) + "[ ]+(.*?[^.\d]{2,})\n", file)
            if result:
                function = result.group(1)
                file.seek(result.end())
            else:
                return None, None

        return function, sub_section_number

    # Append all functions from annex part of file to the list of functions
    # Parameters;
    # file
    # section_number
    # sub_path
    def extract_function(self, file, section_number, sub_path):
        sub_section_number = 1
        function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find first function entry

        while function is not None:  # iterate over function entries

            print "    * " + function.strip()

            if "RSA Files" in function or "Elliptic Curve Files" in function:
                self.handle_RSA_ECC(file, sub_path, section_number, sub_section_number)

            else:

                f = self.extract_code_blocks(file, section_number, sub_section_number, None)

                f.name = function.strip()
                f.short_name = f.name[:-2]
                f.file_name = f.name.replace("()", ".c")
                f.folder_name = sub_path

                self.functions.append(f)

            sub_section_number += 1

            function, sub_section_number = self.next_function(file, section_number, sub_section_number)  # find next function entry

    # Extract section from file
    # Parameters;
    # file
    # name_section
    # name_folder
    def extract_section(self, file, name_section, name_folder):
        # find correct section
        name = name_section.replace("(informative) ", "")
        result = re.search("[ ]+" + name + "\n", file)
        if result:
            file.seek(result.end())
            line = file.readline()
            line = file.readline()
            section_number = re.search("([A-Z])\.", line).group(1)
            print("[+] Section name: {0}".format(name_section))
        else:
            print "Section '" + name_section + "' not found"
            return

        self.extract_function(file, section_number, name_folder)