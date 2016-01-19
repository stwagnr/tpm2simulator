# -*- coding: utf-8 -*-

from textwrap import dedent

from modules import constants
from modules.file_handling import FileHandling


class CommandAttributesHeaderFile:
    """
    """

    # Initializes command attributes header content with according defines
    def __init__(self):
        self.file_path = constants.SRC_PATH + constants.TPM_PATH + "include/CommandAttributes.h"
        self.header_name = "COMMAND_ATTRIBUTES_H"

        '''
        The following template is based on CommandAttributeData.c (see Part 4)
        '''
        self.content = dedent("""\
                                typedef  UINT16             _ATTR_;

                                #define  NOT_IMPLEMENTED   (_ATTR_)(0)
                                #define  ENCRYPT_2         (_ATTR_)(1 <<  0)
                                #define  ENCRYPT_4         (_ATTR_)(1 <<  1)
                                #define  DECRYPT_2         (_ATTR_)(1 <<  2)
                                #define  DECRYPT_4         (_ATTR_)(1 <<  3)
                                #define  HANDLE_1_USER     (_ATTR_)(1 <<  4)
                                #define  HANDLE_1_ADMIN    (_ATTR_)(1 <<  5)
                                #define  HANDLE_1_DUP      (_ATTR_)(1 <<  6)
                                #define  HANDLE_2_USER     (_ATTR_)(1 <<  7)
                                #define  PP_COMMAND        (_ATTR_)(1 <<  8)
                                #define  IS_IMPLEMENTED    (_ATTR_)(1 <<  9)
                                #define  NO_SESSIONS       (_ATTR_)(1 << 10)
                                #define  NV_COMMAND        (_ATTR_)(1 << 11)
                                #define  PP_REQUIRED       (_ATTR_)(1 << 12)
                                #define  R_HANDLE          (_ATTR_)(1 << 13)
                                #define  ALLOW_TRIAL       (_ATTR_)(1 << 14)

                                typedef  _ATTR_            COMMAND_ATTRIBUTES;    // fix for Global.h
                                """)

    # Write contents into header file along with define guards (ifdefs)
    def write(self):
        ifndef = "#ifndef " + self.header_name + "\n"
        define = "#define " + self.header_name + "\n\n"
        endif = "#endif  // " + self.header_name + "\n"

        self.content = ifndef + define + self.content + endif

        FileHandling.write_file(self.file_path, self.content)
