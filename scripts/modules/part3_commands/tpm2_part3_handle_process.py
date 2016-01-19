# -*- coding: utf-8 -*-

import re
from modules import constants
from modules.part3_commands import tpm2_part3_handle_process_templates
from modules.file_handling import FileHandling
from modules import utils
import settings


class HandleProcess:
    """
    """

    def __init__(self):
        self.file = None
        self.file_path = constants.SRC_PATH + constants.TPM_PATH + "/main/HandleProcess.c"
        self.code = ""

        if settings.SPEC_VERSION == "01.16":
            self.command = "TPM_CC          commandCode,  "  # cf. TPM Library Specification, Part 4
            self.selector = "commandCode"
            self.table_driven_dispatch_ifndef = ""
            self.table_driven_dispatch_endif = ""
        else:
            self.command = "COMMAND_INDEX    commandIndex,"  # cf. TPM Library Specification, Part 4
            self.selector = "GetCommandCode(commandIndex)"
            self.table_driven_dispatch_ifndef = "\n#ifndef TABLE_DRIVEN_DISPATCH   //%\n"
            self.table_driven_dispatch_endif = "\n#endif //% TABLE_DRIVEN_DISPATCH\n"

    # Generates inner code for HandleProcess file, using appropriate template
    # Parameters:
    # handle
    # num
    # Returns:
    # generated inner code
    @staticmethod
    def create_inner_code(handle, num):
        inner_code = ""
        bool_text = ""
        handle_with_false_flag = ["TPMI_DH_OBJECT",
                                  "TPMI_RH_ENDORSEMENT",
                                  "TPMI_DH_PCR",
                                  "TPMI_RH_HIERARCHY",
                                  "TPMI_DH_ENTITY"]

        res = re.search('(\w+(_DH_|_RH_)\w+)([\+]*)', handle)

        # plus found?
        if res and res.group(3) == "+":
            handle = res.group(1)
            bool_text = ", TRUE"
        elif res and handle in handle_with_false_flag:  # see __init__
            bool_text = ", FALSE"

        inner_code += "\n"
        inner_code += tpm2_part3_handle_process_templates.handle_process_template_inner.safe_substitute(
            HANDLE=handle,
            NUM=num,
            NUM2=num + 1,
            BOOL=bool_text)

        return inner_code

    # Generates outer code for HandleProcess file, using appropriate template
    # Parameters:
    # function_name
    # num
    # inner_code
    # Returns:
    # generated outer code
    @staticmethod
    def create_outer_code(function_name, num, inner_code):
        func = function_name.replace("TPM2_", "")
        return tpm2_part3_handle_process_templates.handle_process_template_outer.safe_substitute(
            FUNC=func,
            NUM_HANDLES=num,
            EXTENSION=inner_code)

    # Creates case handing for HandleProcess file using inner and outer code generation
    # Parameters:
    # funcname
    # handles
    def create_handle_process_case(self, funcname, handles=None):
        num = 0
        inner_code = ""

        for handle in handles:
            inner_code += self.create_inner_code(handle, num)
            num += 1

        self.code += self.create_outer_code(funcname, num, inner_code)

        return

    # Creates case handing for HandleProcess file using inner and outer code generation
    # Parameters:
    # funcname
    # rows
    def create_handle_process_case_pdf(self, funcname, rows):
        num = 0
        inner_code = ""

        for row in rows:

            if utils.is_handle(row):
                handle = row[0]
                inner_code += self.create_inner_code(handle, num)
                num += 1

        self.code += self.create_outer_code(funcname, num, inner_code)

        return

    # Write contents into HandleProcess file
    def write(self):
        self.code = tpm2_part3_handle_process_templates.handle_process_template.safe_substitute(
            COMMAND=self.command,
            SELECTOR=self.selector,
            TABLE_DRIVEN_DISPATCH_IFNDEF=self.table_driven_dispatch_ifndef,
            TABLE_DRIVEN_DISPATCH_ENDIF=self.table_driven_dispatch_endif,
            CASES=self.code)
        FileHandling.write_file(self.file_path, self.code)
