# -*- coding: utf-8 -*-

from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules.part2_structures.marshal import tpm2_partx_marshal_templates


class ArrayMarshaller(SimpleMarshaller):

    def __init__(self):
        SimpleMarshaller.__init__(self)

    # Generate unmarshal function for arrays
    # Parameters:
    # function - unmarshal type
    # bool_flag - boolean value to decide if additional parameters are needed tor the unmarshal function
    # Returns:
    # generated source code
    def create_unmarshal_code(self, function, bool_flag):

        flag1 = ""
        flag2 = ""

        if bool_flag:
            flag1 = ", BOOL allowNull"
            flag2 = ", allowNull"

        if "BYTE" in function:
            template = tpm2_partx_marshal_templates.BYTE_Array_Unmarshal
        else:
            template = tpm2_partx_marshal_templates.TYPE_Array_Unmarshal

        code = template.safe_substitute(TYPE=function, FLAG1=flag1, FLAG2=flag2)

        return code
    # end of method - create_unmarshal_code(self, function, bool_flag):

    # Generate marshal function for arrays
    # Parameters:
    # function - marshal type
    # Returns:
    # generated source code
    def create_marshal_code(self, function):

        if "BYTE" in function:
            template = tpm2_partx_marshal_templates.BYTE_Array_Marshal
        else:
            template = tpm2_partx_marshal_templates.TYPE_Array_Marshal

        code = template.safe_substitute(TYPE=function)

        return code
    # end of method - create_marshal_code(self, function):

    # Generate unmarshal function prototype for arrays
    # Parameters:
    # mrshl_type - unmarshal type
    # bool_flag - boolean value to decide if additional parameters are needed tor the unmarshal function
    # Returns:
    # generated source code
    @staticmethod
    def create_unmarshal_fp(mrshl_type, bool_flag=False):

        flag = ""

        if bool_flag:
            flag = ", BOOL allowNull"

        template = tpm2_partx_marshal_templates.TYPE_Array_Unmarshal_fp
        code = template.safe_substitute(TYPE=mrshl_type, FLAG=flag)

        return code

    # Generate marshal function prototype for arrays
    # Parameters:
    # mrshl_type - marshal type
    # Returns:
    # generated source code
    @staticmethod
    def create_marshal_fp(mrshl_type):
        template = tpm2_partx_marshal_templates.TYPE_Array_Marshal_fp
        code = template.safe_substitute(TYPE=mrshl_type)

        return code
