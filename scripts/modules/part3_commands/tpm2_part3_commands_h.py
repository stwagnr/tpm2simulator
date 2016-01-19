# -*- coding: utf-8 -*-

from modules import constants
from modules.file_handling import FileHandling


class CommandsHeaderFile:
    """
    """

    def __init__(self):
        self.file_path = constants.SRC_PATH + constants.TPM_PATH + "include/Commands.h"
        self.header_name = "_COMMANDS_H_"

        self.content = u''    # the content of the file
        self.file = None      # the output file handle

    # Appends string to commands header file contents
    # Parameter:
    # content
    def append(self, content):
        self.content += content

    # Writes contents into commands header file
    def write(self):
        ifndef = "#ifndef " + self.header_name + "\n"
        define = "#define " + self.header_name + "\n\n"
        endif = "#endif  // " + self.header_name + "\n"

        self.content = ifndef + define + self.content + endif

        FileHandling.write_file(self.file_path, self.content)
