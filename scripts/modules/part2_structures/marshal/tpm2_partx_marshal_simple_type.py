# -*- coding: utf-8 -*-

from modules.part2_structures.marshal import tpm2_partx_marshal_templates


class SimpleMarshaller:

    def __init__(self):
        pass

    # Generate unmarshal function for simple types
    # Parameters: values used to substitute fields of the template
    # Returns:
    # generated source code
    def create_unmarshal_code(self, mrshl_type, size):
        return_string = tpm2_partx_marshal_templates.RETURN_SUCCESS
        template = tpm2_partx_marshal_templates.TYPE_Unmarshal_simple
        code = template.safe_substitute(TYPE=mrshl_type, SIZE=size, FLAG="",
                                        CODE=tpm2_partx_marshal_templates.Base_Type_Unmarshal_code.safe_substitute(TYPE=mrshl_type, SIZE=size),
                                        RETURN=return_string)
        return code

    # Generate unmarshal function prototype for simple types
    # Parameters:
    # mrshl_type - unmarshal function type
    # bool_flag - boolean value to decide if additional parameters are needed tor the unmarshal function
    # Returns:
    # generated source code
    @staticmethod
    def create_unmarshal_fp(mrshl_type, bool_flag=False):

        flag = ""
        if bool_flag:
            flag = ", BOOL allowNull"

        template = tpm2_partx_marshal_templates.TYPE_Unmarshal_simple_fp
        code = template.safe_substitute(TYPE=mrshl_type, FLAG=flag)
        return code

    # Generate unmarshal function prototype definition for simple types
    # Parameters:
    # mrshl_type - unmarshal function type
    # to_type - unmarshal function type to define to
    # Returns:
    # generated source code
    @staticmethod
    def create_unmarshal_fp_define(mrshl_type, to_type):
        template = tpm2_partx_marshal_templates.TYPE_Unmarshal_structure_fp_define
        code = template.safe_substitute(TYPE=mrshl_type, TO_TYPE=to_type, VAR="(target)", FLAG="")
        return code

    # Generate marshal function for simple types
    # Parameters: values used to substitute fields of the templates
    # Returns:
    # generated source code
    @staticmethod
    def create_marshal_code(mrshl_type, size):
        template = tpm2_partx_marshal_templates.TYPE_Marshal_simple
        code = template.safe_substitute(TYPE=mrshl_type, SIZE=size,
                                        CODE=tpm2_partx_marshal_templates.Base_Type_Marshal_code.safe_substitute(TYPE=mrshl_type, SIZE=size))
        return code

    # Generate marshal function prototype for simple types
    # Parameters:
    # mrshl_type - marshal function type
    # Returns:
    # generated source code
    @staticmethod
    def create_marshal_fp(mrshl_type):
        template = tpm2_partx_marshal_templates.TYPE_Marshal_simple_fp
        code = template.safe_substitute(TYPE=mrshl_type)
        return code

    # Generate marshal function prototype definition for simple types
    # Parameters:
    # mrshl_type - marshal function type
    # to_type - marshal function type to define to
    # Returns:
    # generated source code
    @staticmethod
    def create_marshal_fp_define(mrshl_type, to_type):
        template = tpm2_partx_marshal_templates.TYPE_Marshal_simple_fp_define
        code = template.safe_substitute(TYPE=mrshl_type, TO_TYPE=to_type, VAR="(source)")
        return code
