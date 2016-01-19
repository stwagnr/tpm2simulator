# -*- coding: utf-8 -*-

import re

from modules.prototypes.tpm2_partx_prototype_file import PrototypeFile
from modules.file_handling import FileHandling
from modules import data_structures
from modules.part3_commands.tpm2_part3_commands_fp import CommandsPrototypeFile


class SupportRoutinesPrototypeFile(PrototypeFile):

    # Extracts prototypes from support routine file
    # Parameters:
    # function
    def extract_prototype_functions(self, function):
        add_to_proto = True
        commands_fp = False

        iterator = iter(function.elements)
        for element in iterator:

            if not isinstance(element, data_structures.TPM2_Partx_CodeLine):
                continue

            code_line = element  # element is CodeLine

            if code_line.string.startswith("//%"):
                self.functions.append(code_line.string.replace("//%", "") + '\n')
                continue

            if "//%" in code_line.string:
                self.functions.append(code_line.string + '\n')
                continue

            # skip static functions
            result = re.search("^[ ]*static|[ ]+s_", code_line.string)
            if result and "//%" not in code_line.string:
                if not code_line.string.endswith(";"):
                    add_to_proto = False
                continue

            # skip typedefs
            result = re.search("^[ ]*typedef", code_line.string)
            if result and "//%" not in code_line.string:
                if "struct" in code_line.string or "union" in code_line.string:
                    while not code_line.string.startswith("}"):
                        element = next(iterator, None)
                        code_line = element
                continue

            # skip includes
            result = re.search("(#([\s]*)(include|define|pragma)|FAIL)", code_line.string)
            if result and "//%" not in code_line.string:
                continue

            if "CommandCapGetCCList" in code_line.string:
                commands_prototype_file = CommandsPrototypeFile()
                commands_prototype_file.append("TPMI_YES_NO\n") # previous line (return type) was skipped, add too
                commands_fp = True

            if add_to_proto:

                if code_line.string.strip() == "{":

                    add_to_proto = False
                    self.functions.content = self.functions.content[:-1]
                    self.functions.append(';\n\n')
                    if commands_fp:
                        commands_prototype_file.content = commands_prototype_file.content[:-1]
                        commands_prototype_file.append(';\n\n')
                        commands_prototype_file.write()
                        commands_fp = False

                else:

                    self.functions.append(code_line.string.replace("//%", "") + "\n")

                    if commands_fp:
                        commands_prototype_file.append(code_line.string.replace("//%", "") + "\n")

            elif code_line.string == "}" or code_line.string == "};":
                add_to_proto = True
                commands_fp = False

    # Writes support routine prototype into file at file_path
    def write(self):
        ifndef = "#ifndef " + self.header_name_sup + "\n"
        define = "#define " + self.header_name_sup + "\n\n"
        endif = "#endif  // " + self.header_name_sup + "\n"

        file_content = ifndef + define + self.functions.content + endif

        FileHandling.write_file(self.file_path, file_content)
