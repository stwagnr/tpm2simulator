# -*- coding: utf-8 -*-

from modules import comment, constants
import re


class ExtractionNavigator(object):
    """
    """

    def __init__(self):
        self.COMMAND_PATH = constants.SRC_PATH + constants.TPM_PATH + "command/"
        self.comments = comment.Comment()
        self.functions = []

    # Extracts section according to given name
    # Parameters:
    # file
    # name_section
    # name_folder
    def extract_section(self, file, name_section, name_folder):
        # find correct section
        name = name_section.replace("(", "\(")
        name = name.replace(")", "\)")
        result = re.search("(\d{1,2})[ ]+" + name + "\n", file)
        if result:
            section_number = result.group(1)
            file.seek(result.start())
            line = file.readline()
            print("[+] Section name: {0}".format(name_section))
        else:
            print "Section '" + name_section + "' not found"
            return

        self.extract_function(file, section_number, name_folder)

    # Function not implemented
    def extract_function(self, file, section_number, name_folder):
        """ 
        interface 'extract_function' must be implemented by the child class or mixin
        """
        raise NotImplementedError("[-] 'extract_function' not yet implemented...")

    # Function not implemented
    def next_function(self, file, section_number, sub_section_number):
        """ 
        interface 'next_function' must be implemented by the child class or mixin
        """
        raise NotImplementedError("[-] 'next_function' not yet implemented...")

    # Function not implemented
    def next_entry(self, file, entry, section):
        """ 
        interface 'next_entry' must be implemented by the child class or mixin
        """
        raise NotImplementedError("[-] 'next_entry' not yet implemented...")

    # Extracts all functions from pdf file
    # Parameters:
    # file
    # folders
    # Returns:
    # list of functions
    def extract_pdf(self, file, folders):
        for section in folders:
            self.extract_section(file, section, folders[section])
        return self.functions
