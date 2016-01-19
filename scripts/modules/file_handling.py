import codecs
import mmap

from bs4 import BeautifulSoup
import os
import re
from modules import constants


class FileHandling(object):
    """
    """

    license = ""
    warn_pyastyle = False

    def __init__(self):
        pass
      
    # Assigns license string to the current file
    # Parameters:
    # string - contains license string
    @staticmethod
    def set_license(string):
        FileHandling.license = string

    # Opens file with the specified filename and returns its file descriptor.
    # Distinguishes between .txt files (opens them and maps them into memory with the exact content)
    # and .fodt files (opens them with BeautifulSoup, so they can be parsed for XML tags)
    # Parameters:
    # file_name - name of the file to be opened
    # Returns:
    # fd - file descriptor of opened file
    def get_fd(self, file_name):
        fd = None
        if file_name.endswith(".txt"):
            f = codecs.open(file_name, "r", constants.UTF8)
            fd = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        elif file_name.endswith(".fodt"):
            f = open(file_name)
            fd = BeautifulSoup(f, constants.PARSER)
        return fd

    # Creates file at specified path, and writes the content string into it, formatted with astyle
    # Parameters:
    # file_path - path of the file to be created
    # content - string to be written into created file
    @staticmethod
    def write_file(file_path, content):
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        f = codecs.open(file_path, "w", constants.UTF8)

        try:
            import pyastyle

            content = re.sub("(?![ ]*\/)[ ]{2,}", " ", content)
            content = pyastyle.format(content, "")
        except ImportError:
            FileHandling.warn_pyastyle = True

        f.write(FileHandling.license)
        f.write("\n")
        f.write(content)
        f.close()
        return
