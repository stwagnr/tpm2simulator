# -*- coding: utf-8 -*-

import re

from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules.part2_structures.marshal import tpm2_partx_marshal_templates as MarshalTemplates
import settings

class StructureTableMarshaller(SimpleMarshaller):

    def __init__(self):
        SimpleMarshaller.__init__(self)

    @staticmethod
    def extract_constraints(cell):
        result = re.search('{([\w()_]*)\s*:\s*([\w()_/2]*)}', cell)
        if result:
            return result.group(1), result.group(2)
        else:
            return None, None

    @staticmethod
    def extract_concatenations(cell):
        result = re.search('{([\w()_]*),\s*([\w()_]*)}', cell)
        if result:
            return result.group(1), result.group(2)
        else:
            return None, None

    # Generate unmarshal function for every entry of a StructureTable
    # Parameters:
    # mrshl_type - unmarshal function type
    # table - internal representation of StructureTable, where the first column represents a structure member, and the
    #         second column the type of unmarshal function
    # function_prototypes_with_flag
    # Returns:
    # generated source code
    def create_unmarshal_code(self, mrshl_type, table, function_prototypes_with_flag):

        flag = ""
        code = "TPM_RC    rc = TPM_RC_SUCCESS;\n"
        rc_fail = "TPM_RC_SIZE"
        return_string = "return rc;"
        sizefield = False

        structure = "t."
        if mrshl_type.startswith("TPMS") or mrshl_type.startswith("TPMT") or mrshl_type.startswith("TPML") or \
                (settings.SPEC_VERSION_INT>=138 and table.rows[0][0].endswith("=")):
            structure = ""

        # FIX: There is no "=" after size in row 1
        if "TPM2B_SENSITIVE Structure" in table.name and settings.SPEC_VERSION_INT>=138:
            structure = ""

        for row in table.rows:
            parameter = row[0]
            if parameter.startswith("#"):
                rc_fail = parameter.replace("#", "")

        for row in table.rows:
            parameter = row[0]
            to_type = row[1].strip()

            if parameter.startswith("//") or parameter.startswith("#"):
                continue

            if to_type.startswith("+"):
                flag = ", BOOL     allowNull"
                to_type = to_type.replace("+", "")

                code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                    MEMBER=structure + parameter,
                                                                                    TO_MEMBER=", allowNull")
                if sizefield:
                    code += MarshalTemplates.if_success_execute.safe_substitute(
                        COMMAND=MarshalTemplates.check_struct_size.safe_substitute(STRUCT=structure))
                    return_string = MarshalTemplates.RETURN_SUCCESS
                continue

            ''' CONSTRAINTS AND ARRAY SIZE IN 1ST COLUMN '''
            result = re.search('^\[(.*)\]\s*([\w]+)', parameter)
            if result:
                to_member = ", (UINT32)(target->" + result.group(1) + ")"
                struct_member = result.group(2)

                code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                    MEMBER=structure + struct_member,
                                                                                    TO_MEMBER=to_member)
                continue

            result = re.search('([\w]+)[\s]*\[(.*)\][\s]*({.*})*', parameter)
            if result:
                struct_member = result.group(1)

                if to_type in function_prototypes_with_flag.keys():
                    to_member = ", 0, (INT32)(target->" + structure + result.group(2) + ")"
                else:
                    to_member = ", (INT32)(target->" + structure + result.group(2) + ")"

                minimum, maximum = self.extract_constraints(result.group(3))
                if minimum:
                    code += MarshalTemplates.comparison_check.safe_substitute(MEMBER=structure + result.group(2),
                                                                              SIGN="<",
                                                                              COMPARE_TO=minimum,
                                                                              RC_FAIL=rc_fail)
                if maximum:
                    code += MarshalTemplates.comparison_check.safe_substitute(MEMBER=structure + result.group(2),
                                                                              SIGN=">",
                                                                              COMPARE_TO=maximum,
                                                                              RC_FAIL=rc_fail)

                code += MarshalTemplates.call_TYPE_array_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                          MEMBER=structure + struct_member,
                                                                                          TO_MEMBER=to_member)
                continue

            ''' CONSTRAINTS, BUT NO ARRAY SIZE IN 1ST COLUMN '''
            result = re.search('([\w_]+)([\s]*)({.*})', parameter)
            if result:
                struct_member = result.group(1)

                code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                    MEMBER=structure + struct_member,
                                                                                    TO_MEMBER="")

                minimum, maximum = self.extract_constraints(result.group(3))
                if minimum:
                    code += MarshalTemplates.comparison_check.safe_substitute(MEMBER=structure + struct_member,
                                                                              SIGN="<",
                                                                              COMPARE_TO=minimum,
                                                                              RC_FAIL=rc_fail)
                if maximum:
                    code += MarshalTemplates.comparison_check.safe_substitute(MEMBER=structure + struct_member,
                                                                              SIGN=">",
                                                                              COMPARE_TO=maximum,
                                                                              RC_FAIL=rc_fail)

                if minimum is None and maximum is None:
                    first, second = self.extract_concatenations(result.group(3))
                    # same as in TSS
                    if first and second:
                        code += "    if( ((target->" + structure + struct_member + ") != " + first + ")\n"
                        code += "     && ((target->" + structure + struct_member + ") != " + second + "))\n"
                    else:
                        result = re.search('{(.*)}', parameter)
                        code += "    if( ((target->" + structure + struct_member + ") != " + result.group(1) + "))\n"

                    code += "       return " + rc_fail + ";\n"
                continue

            struct_member = parameter

            ''' NO CONSTRAINTS OR ARRAY SIZE IN 1ST COLUMN '''
            if struct_member.endswith("="):
                sizefield = True
                code += "    INT32    startSize;\n"

                code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                    MEMBER=structure + struct_member[:-1],
                                                                                    TO_MEMBER="")
                code += MarshalTemplates.size_zero_check.safe_substitute(STRUCT=structure,
                                                                         RETURN="TPM_RC_SIZE")
                code += "    startSize = *size;\n"

            elif to_type.replace("+", "") in function_prototypes_with_flag.keys():
                if to_type.endswith("+"):
                    to_type = to_type.strip().replace("+", "")

                    code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                        MEMBER=structure + struct_member,
                                                                                        TO_MEMBER=", 1")

                else:
                    code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                        MEMBER=structure + struct_member,
                                                                                        TO_MEMBER=", 0")
            else:
                if "TPM2B_SENSITIVE Structure" in table.name and struct_member == "size":
                    code += "    INT32    startSize;\n"

                code += MarshalTemplates.call_TYPE_unmarshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                    MEMBER=structure + struct_member,
                                                                                    TO_MEMBER="")

                if sizefield:
                    code += MarshalTemplates.if_success_execute.safe_substitute(
                        COMMAND=MarshalTemplates.check_struct_size.safe_substitute(STRUCT=structure))
                    return_string = MarshalTemplates.RETURN_SUCCESS

            if struct_member == "size":
                code += MarshalTemplates.size_zero_check.safe_substitute(STRUCT=structure,
                                                                         RETURN="TPM_RC_SUCCESS")
                if "TPM2B_SENSITIVE Structure" in table.name:
                    code += "    startSize = *size;\n"

            # FIX: There is no "=" after size in row 1
            if "TPM2B_SENSITIVE Structure" in table.name and struct_member != "size":
                code += MarshalTemplates.if_success_execute.safe_substitute(
                    COMMAND=MarshalTemplates.check_struct_size.safe_substitute(STRUCT=structure))
                return_string = MarshalTemplates.RETURN_SUCCESS
        # end of loop - for row in table.rows:

        code = code[:-1]

        template = MarshalTemplates.TYPE_Unmarshal_simple

        code = template.safe_substitute(TYPE=mrshl_type, FLAG=flag, CODE=code, RETURN=return_string)

        return code
    # end of method - create_unmarshal_code(self, mrshl_type, table, function_prototypes_with_flag):

    # Generate marshal function for every entry of a StructureTable
    # Parameters:
    # mrshl_type - marshal function type
    # table - internal representation of StructureTable, where the first column represents a structure member, and the
    #         second column the type of marshal function
    # function_prototypes_with_flag
    # Returns:
    # generated source code
    def create_marshal_code(self, mrshl_type, table, function_prototypes_with_flag):
        flag = ""
        code = "UINT16    written = 0;\n"
        sizefield = False

        structure = "t."
        if mrshl_type.startswith("TPMS") or mrshl_type.startswith("TPMT") or mrshl_type.startswith("TPML") or \
                (settings.SPEC_VERSION_INT >= 138 and table.rows[0][0].endswith("=")):
            structure = ""

        # FIX: There is no "=" after size in row 1
        if "TPM2B_SENSITIVE Structure" in table.name and settings.SPEC_VERSION_INT>=138:
            structure = ""

        for row in table.rows:
            parameter = row[0]
            to_type = row[1].strip()

            if parameter.startswith("//") or parameter.startswith("#"):
                continue

            if "+" in to_type:
                flag = ", BOOL     allowNull"
                to_type = to_type.replace("+", "")

                code += MarshalTemplates.call_TYPE_marshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                  MEMBER=structure + parameter,
                                                                                  TO_MEMBER="")
                if sizefield:
                    code += MarshalTemplates.call_marshal_size.safe_substitute()
                continue

            ''' CONSTRAINTS AND ARRAY SIZE IN 1ST COLUMN '''
            result = re.search('^\[(.*)\]\s*([\w]+)', parameter)
            if result:
                to_member = ", (UINT32)(source->" + result.group(1) + ")"
                struct_member = result.group(2)

                code += MarshalTemplates.call_TYPE_marshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                  MEMBER=structure + struct_member,
                                                                                  TO_MEMBER=to_member)
                continue

            result = re.search('([\w]+)[\s]*\[(.*)\][\s]*({.*})*', parameter)
            if result:
                to_member = ", (INT32)(source->" + structure + result.group(2)  + ")"
                struct_member = result.group(1)

                code += MarshalTemplates.call_TYPE_array_marshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                        MEMBER=structure + struct_member,
                                                                                        TO_MEMBER=to_member)
                continue

            struct_member = parameter

            ''' CONSTRAINTS, BUT NO ARRAY SIZE IN 1ST COLUMN '''
            result = re.search('([\w_]+)([\s]*)({.*})', struct_member)
            if result:
                struct_member = result.group(1)
                code += MarshalTemplates.call_TYPE_marshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                  MEMBER=struct_member,
                                                                                  TO_MEMBER="")
                continue

            ''' NO CONSTRAINTS OR ARRAY SIZE IN 1ST COLUMN '''
            if struct_member.endswith("="):
                sizefield = True
                code += "    BYTE      *sizeField = *buffer;\n"
                code += "    *buffer += 2;\n"
            elif to_type.replace("+", "") in function_prototypes_with_flag.keys():
                code += MarshalTemplates.call_TYPE_marshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                  MEMBER=structure + struct_member,
                                                                                  TO_MEMBER="")
            else:
                code += MarshalTemplates.call_TYPE_marshal_struct.safe_substitute(TO_TYPE=to_type,
                                                                                  MEMBER=structure + struct_member,
                                                                                  TO_MEMBER="")
                if sizefield:
                    code += MarshalTemplates.call_marshal_size.safe_substitute()

            if parameter == "size":
                code += "    if(source->"+structure+"size == 0)\n"
                code += "        return written;\n\n"

        code += "    return written;\n"

        code = code[:-1]

        template = MarshalTemplates.TYPE_Marshal_simple

        code = template.safe_substitute(TYPE=mrshl_type, FLAG=flag, CODE=code)

        return code
    # end of method - create_marshal_code(self, mrshl_type, table, function_prototypes_with_flag):

    # Generate unmarshal function prototype for an entry of a StructureTable
    # Parameters:
    # mrshl_type - unmarshal function type
    # bool_flag - boolean value to decide if additional parameters are needed tor the unmarshal function
    # Returns:
    # generated source code
    def create_unmarshal_fp(self, mrshl_type, bool_flag=False):

        flag = ""
        if bool_flag:
            flag = ", BOOL allowNull"

        template = MarshalTemplates.TYPE_Unmarshal_simple_fp
        code = template.safe_substitute(TYPE=mrshl_type, FLAG=flag)

        return code

    # Generate unmarshal function prototype definition for an entry of a StructureTable
    # Parameters:
    # mrshl_type - current unmarshal function type
    # to_type - unmarshal function type to define to
    # var - structure member
    # Returns:
    # generated source code
    def create_unmarshal_fp_define(self, mrshl_type, to_type, var, f=-1):

        if var:
            var = "&((target)->" + var + ")"
        else:
            var = "(target)"

        flag = ""
        if f == 0:
            flag = ", 0"
        elif f == 1:
            flag = ", 1"

        template = MarshalTemplates.TYPE_Unmarshal_structure_fp_define
        code = template.safe_substitute(TYPE=mrshl_type, TO_TYPE=to_type, VAR=var, FLAG=flag)

        return code

    # Generate marshal function prototype for an entry of a StructureTable
    # Parameters:
    # mrshl_type - marshal function type
    # Returns:
    # generated source code
    def create_marshal_fp(self, mrshl_type):

        template = MarshalTemplates.TYPE_Marshal_simple_fp
        code = template.safe_substitute(TYPE=mrshl_type)

        return code

    # Generate marshal function prototype definition for an entry of a StructureTable
    # Parameters:
    # mrshl_type - current marshal function type
    # to_type - marshal function type to define to
    # var - structure member
    # Returns:
    # generated source code
    def create_marshal_fp_define(self, mrshl_type, to_type, var, f=-1):

        if var:
            var = "&((source)->" + var + ")"
        else:
            var = "(source)"

        template = MarshalTemplates.TYPE_Marshal_simple_fp_define
        code = template.safe_substitute(TYPE=mrshl_type, TO_TYPE=to_type, VAR=var)

        return code
