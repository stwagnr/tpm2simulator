# -*- coding: utf-8 -*-

from modules import constants
from modules.file_handling import FileHandling
from modules.part3_commands import tpm2_part3_command_dispatcher_templates
import settings


class CommandDispatcher:

    # Generates boolean parameter to a function according to given type
    # Parameters:
    # to_type
    # Returns:
    # string containing appropriate boolean parameter or empty string, if parameter not needed
    @staticmethod
    def set_bool_text(to_type):
        bool_text = ""
        if "+" in to_type:
            bool_text = ", TRUE"
        elif to_type in ["TPMI_DH_OBJECT",
                         "TPMI_RH_ENDORSEMENT",
                         "TPMI_DH_PCR",
                         "TPMI_RH_HIERARCHY",
                         "TPMI_DH_ENTITY",
                         "TPMI_RH_ENABLES",
                         "TPMI_ALG_HASH",
                         "TPMI_ECC_KEY_EXCHANGE",
                         "TPMT_SIGNATURE",
                         "TPM2B_PUBLIC"]:
            bool_text = ", FALSE"
        return bool_text

    # Initializes the member variables of the class according to type of file the simulator code is extracted from
    def __init__(self):
        self.code = ""
        self.file = None
        self.file_path = constants.SRC_PATH + constants.TPM_PATH + "/main/CommandDispatcher.c"

        if settings.DATA_ORIGIN_PDF_TXT:
            self.command = "TPM_CC                  commandCode,"
            self.command_var = "commandCode"
            self.selector = "commandCode"
        else:
            self.command = "COMMAND_INDEX           commandIndex,"
            self.command_var = "commandIndex"
            self.selector = "GetCommandCode(commandIndex)"

    # Creates command dispatcher unmarshal handle
    # function_name
    # param
    # num
    # Returns:
    # generated unmarshal handle
    def create_command_dispatcher_unmarshal_handle(self, function_name, param, num):
        function_name = function_name.replace("TPM2_", "")
        return tpm2_part3_command_dispatcher_templates.template_unmarshal_handle.safe_substitute(FUNC=function_name, PARAM=param, NUM=num)

    # Creates command dispatcher unmarshal code
    # function_name
    # to_type
    # param
    # Returns:
    # generated unmarshal code
    def create_command_dispatcher_unmarshal(self, function_name, to_type, param):
        function_name = function_name.replace("TPM2_", "")
        bool_text = self.set_bool_text(to_type)
        to_type = to_type.replace("+", "")  # cleanup any "+" that might be in to_type
        return tpm2_part3_command_dispatcher_templates.template_unmarshal.safe_substitute(FUNC=function_name, TO_TYPE=to_type, PARAM=param, BOOL=bool_text)

    # Creates command dispatcher marshal handle
    # function_name
    # param
    # num
    # Returns:
    # generated marshal handle
    def create_command_dispatcher_marshal_handle(self, function_name, to_type, param):
        function_name = function_name.replace("TPM2_", "")
        return tpm2_part3_command_dispatcher_templates.template_marshal_handle.safe_substitute(FUNC=function_name, TO_TYPE=to_type, PARAM=param)

    # Creates command dispatcher marshal code
    # function_name
    # to_type
    # param
    # Returns:
    # generated marshal handle
    def create_command_dispatcher_marshal(self, function_name, to_type, param):
        function_name = function_name.replace("TPM2_", "")
        return tpm2_part3_command_dispatcher_templates.template_marshal.safe_substitute(FUNC=function_name, TO_TYPE=to_type, PARAM=param)

    # Adds cases handling to the code of the command dispatcher
    def create_command_dispatcher_case(self, function_name, bool_in_params, bool_out_params, handles, unmarshal, marshal):

        inout = ""

        in_params = "// No buffer for input parameters required"
        if bool_in_params:
            in_params = tpm2_part3_command_dispatcher_templates.template_in_params.safe_substitute(FUNC=function_name)
            inout = "in_params"

        out_params = "// No buffer for output parameters required"
        if bool_out_params:
            out_params = tpm2_part3_command_dispatcher_templates.template_out_params.safe_substitute(FUNC=function_name)
            inout = "out_params"

        if bool_in_params and bool_out_params:
            inout = "in_params, out_params"

        if marshal:
            marshal = "// Calculate size of " + function_name + "_Out\n" \
                      "                size = sizeof(" + function_name + "_Out);\n\n" \
                      "                " + marshal

        function_name = function_name.replace("TPM2_", "")
        action_routine = tpm2_part3_command_dispatcher_templates.template_action_routine.safe_substitute(
            FUNC=function_name,
            INOUT=inout)

        if handles is "":
            handles = "// No handles required"

        self.code += tpm2_part3_command_dispatcher_templates.template_outer.safe_substitute(FUNC=function_name,
                                                   IN_PARAMS=in_params,
                                                   OUT_PARAMS=out_params,
                                                   HANDLES=handles,
                                                   UNMARSHAL=unmarshal,
                                                   ACTION_ROUTINE=action_routine,
                                                   MARSHAL=marshal)
        return

    # Writes formatted contents of command dispatcher into file
    def write(self):
        self.code = tpm2_part3_command_dispatcher_templates.command_dispatcher_template.safe_substitute(
            COMMAND=self.command,
            COMMAND_VAR=self.command_var,
            SELECTOR=self.selector,
            CASES=self.code)

        FileHandling.write_file(self.file_path, self.code)
