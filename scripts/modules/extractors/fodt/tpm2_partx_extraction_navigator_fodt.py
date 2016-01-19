# -*- coding: utf-8 -*-

# custom stuff:
from bs4 import Tag

from modules import comment, constants


class ExtractionNavigator(object):
    """
    """

    def __init__(self):
        self.COMMAND_PATH = constants.SRC_PATH + constants.TPM_PATH + "command/"
        self.comments = comment.Comment()
        self.functions = []

    # The selector function mainly serves the purpose of finding the next tag,
    # whose string is a part of the code module (it will be interpreted as a
    # comment). Hence, the selector looks for valid tags including the
    # 'text:list', 'text:p', and 'table:table' tags. In case the tag is of type
    # 'text:p', the selector additionally looks for the text-style of type
    # 'Text_', representing an outlined comment within the code.
    @staticmethod
    def selector(tag):
        """
        """

        if isinstance(tag, Tag):
            if tag.name == constants.XML_TEXT_LIST:
                return True
            elif (tag.name == constants.XML_TEXT_P
                    and tag.has_attr(constants.XML_TEXT_STYLE_NAME)
                    and "Text_" in tag[constants.XML_TEXT_STYLE_NAME]):
                return True
            elif tag.name == constants.XML_TABLE_TABLE:
                return True

        return False

    # Extracts section according to given name
    # Parameters:
    # entry
    # name_section
    # name_folder
    def extract_section(self, entry, name_section, name_folder):
        # find correct section
        while isinstance(entry, Tag) and entry.get_text().strip() != name_section:
            entry = entry.find_next(constants.XML_TEXT_H, {constants.XML_TEXT_OUTLINE_LEVEL: '1'})

        # couldn't find the right section
        if entry is None:
            return

        print("[+] Section name: {0}".format(entry.get_text().strip()))

        self.extract_function(entry, name_section, name_folder)

    # Function not implemented
    def extract_function(self, main_entry, name_section, name_folder):
        """ 
        interface 'extract_function' must be implemented by the child class or mixin
        """
        raise NotImplementedError("[-] 'extract_function' not yet implemented...")

    # Function not implemented
    def next_function(self, entry):
        """ 
        interface 'next_function' must be implemented by the child class or mixin
        """
        raise NotImplementedError("[-] 'next_function' not yet implemented...")

    # Function not implemented
    def next_entry(self, entry):
        """ 
        interface 'next_entry' must be implemented by the child class or mixin
        """
        raise NotImplementedError("[-] 'next_entry' not yet implemented...")

    # Extracts all functions from xml file
    # Parameters:
    # xml
    # folders
    # Returns:
    # list of functions
    def extract_fodt(self, xml, folders):

        entry = xml.find(constants.XML_TEXT_H, {constants.XML_TEXT_OUTLINE_LEVEL: '1'})

        for section in folders:
            self.extract_section(entry, section, folders[section])

        return self.functions

