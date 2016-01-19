# -*- coding: utf-8 -*-

import re

from modules.part2_structures import tpm2_part2_structures_alg_ids
from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules import utils
from modules.part2_structures.marshal import tpm2_partx_marshal_templates as MarshalTemplates


class UnionTableMarshaller(SimpleMarshaller):

    def __init__(self):
        SimpleMarshaller.__init__(self)

    # Generate unmarshal function for every entry of a UnionTable
    # Parameters:
    # mrshl_type - unmarshal function type
    # rows - rows of a UnionTable, where the first column represents a union member, and the
    #         second column the type of unmarshal function
    # tpm_alg_ids -  mapping from algorithm types to list of corresponding algorithm IDs
    # function_prototypes_with_flag
    # Returns:
    # generated source code
    def create_unmarshal_code(self, mrshl_type, rows, tpm_alg_ids, function_prototypes_with_flag):

        cases_list = []
        alg_list = []
        algs_string = ""

        for row in rows:
            parameter = row[0]
            tpm_type = row[1].replace("+", "").upper()
            selector = row[2]

            if selector is None:
                selector = ""

            if "null" in parameter:
                cases_list.append(row)
                continue

            result = re.search('TPM_ALG_', selector)
            if result is not None:
                if selector.endswith("!ALG"):  # fix for 2:144
                    selector = "TPM_ALG_" + parameter
                
                if "!ALG" in selector:
                    alg_list += utils.expand_alg_macro(selector, tpm_alg_ids)
                else:
                    alg_list += [tpm2_part2_structures_alg_ids.AlgorithmID(selector.upper(), "", "", "")]

                for alg in alg_list:
                    full_alg_name = alg.name
                    alg_name = utils.extract_alg_name(full_alg_name)

                    algs_string += "#ifdef    " + full_alg_name + "\n"
                    algs_string += "        case " + full_alg_name + ":\n"

                    if "TPM2B_" in tpm_type:
                        alg_key = selector.replace("TPM_ALG_", "").upper()
                        tpm_type_final = tpm_type.replace(alg_key, alg_name.upper())

                        algs_string += MarshalTemplates.return_type_unmarshal.safe_substitute(TO_TYPE=tpm_type_final,
                                                                                              MEMBER=parameter,
                                                                                              TO_MEMBER="")

                    elif "TPMI_" in tpm_type or "TPMS_" in tpm_type or "TPMT_" in tpm_type:
                        alg_key = selector.replace("TPM_ALG_", "").upper()
                        tpm_type_final = tpm_type.replace(alg_key, alg_name.upper())
                        # in table 144 the part that needs to be removed differs from alg_key
                        if re.search('!ALG', tpm_type_final):
                            tpm_type_final = tpm_type_final.replace('!ALG', alg_name.upper())

                        if "!ALG" in parameter:
                            parameter_final = alg_name.lower()
                        else:
                            parameter_final = parameter

                        to_member = ""
                        if tpm_type_final in function_prototypes_with_flag.keys():
                            to_member = ", 0"

                        algs_string += MarshalTemplates.return_type_unmarshal.safe_substitute(TO_TYPE=tpm_type_final,
                                                                                              MEMBER=parameter_final,
                                                                                              TO_MEMBER=to_member)

                    else:
                        if len(tpm_type) == 0:
                            algs_string += "            " + MarshalTemplates.RETURN_SUCCESS + "\n"
                        else:
                            algs_string += MarshalTemplates.return_array_unmarshal.safe_substitute(TO_TYPE=tpm_type,
                                                                                                   MEMBER=alg_name.lower(),
                                                                                                   TO_MEMBER=", (INT32)" + alg_name.upper() + "_DIGEST_SIZE")
                    algs_string += "#endif // " + full_alg_name + "\n"

                # end of loop - for alg in alg_list:
                alg_list = []
                continue

            if len(selector) > 0:
                cases_list.append(row)
        # end of loop - for row in rows:

        # CASES
        cases_string = ""
        for case in cases_list:
            cases_string += "        case " + case[2] + ":\n"
            cases_string += "            " + MarshalTemplates.RETURN_SUCCESS + "\n"
        cases_string = cases_string[:-1]

        code = MarshalTemplates.TYPE_Unmarshal_union.safe_substitute(TYPE=mrshl_type,
                                                                     CASES=cases_string,
                                                                     ALGS=algs_string)

        return code
    # end of method - create_unmarshal_code(self, mrshl_type, rows, tpm_alg_ids, function_prototypes_with_flag):

    # Generate marshal function for every entry of a UnionTable
    # Parameters:
    # mrshl_type - marshal function type
    # rows - rows of a UnionTable, where the first column represents a union member, and the
    #         second column the type of marshal function
    # tpm_alg_ids -  mapping from algorithm types to list of corresponding algorithm IDs
    # function_prototypes_with_flag
    # Returns:
    # generated source code
    def create_marshal_code(self, mrshl_type, rows, tpm_alg_ids, function_prototypes_with_flag):

        algs_string = ""
        cases_list = []
        alg_list = []

        for row in rows:
            parameter = row[0]
            tpm_type = row[1].replace("+", "")
            selector = row[2]

            if selector is None:
                selector = ""

            if "null" in parameter:
                cases_list.append(row)
                continue

            result = re.search('TPM_ALG_', selector)
            if result is not None:
                if selector.endswith("!ALG"):  # fix for 2:144
                    selector = "TPM_ALG_" + parameter

                if "!ALG" in selector:
                    alg_list += utils.expand_alg_macro(selector, tpm_alg_ids)
                else:
                    alg_list += [tpm2_part2_structures_alg_ids.AlgorithmID(selector.upper(), "", "", "")]

                for alg in alg_list:
                    full_alg_name = alg.name
                    alg_name = utils.extract_alg_name(full_alg_name)

                    algs_string += "#ifdef    " + full_alg_name + "\n"
                    algs_string += "        case " + full_alg_name + ":\n"

                    if "TPM2B_" in tpm_type:
                        alg_key = selector.replace("TPM_ALG_", "").upper()
                        tpm_type_final = tpm_type.replace(alg_key, alg_name.upper())

                        algs_string += MarshalTemplates.return_type_marshal.safe_substitute(TO_TYPE=tpm_type_final,
                                                                                            MEMBER=parameter,
                                                                                            TO_MEMBER="")

                    elif "TPMI_" in tpm_type or "TPMS_" in tpm_type or "TPMT_" in tpm_type:
                        alg_key = selector.replace("TPM_ALG_", "")
                        tpm_type_final = tpm_type.replace(alg_key, alg_name.upper())
                        # in table 144 the part that needs to be removed differs from alg_key
                        if re.search('!ALG', tpm_type_final):
                            tpm_type_final = tpm_type_final.replace('!ALG', alg_name.upper())

                        if "!ALG" in parameter:
                            parameter_final = alg_name.lower()
                        else:
                            parameter_final = parameter

                        algs_string += MarshalTemplates.return_type_marshal.safe_substitute(TO_TYPE=tpm_type_final,
                                                                                            MEMBER=parameter_final,
                                                                                            TO_MEMBER="")
                    else:
                        if len(tpm_type) == 0:
                            algs_string += "            return 0;\n"
                        else:
                            algs_string += MarshalTemplates.return_array_marshal.safe_substitute(TO_TYPE=tpm_type,
                                                                                                 MEMBER=alg_name.lower(),
                                                                                                 TO_MEMBER=", (INT32)" + alg_name.upper() + "_DIGEST_SIZE")
                    algs_string += "#endif // " + full_alg_name + "\n"
                # end of loop - for alg in alg_list:

                alg_list = []
                continue

            if len(selector) > 0:
                cases_list.append(row)

        cases_string = ""
        # CASES
        for case in cases_list:
            parameter = case[0]
            tpm_type = case[1]
            selector = case[2]

            if "null" in parameter:
                cases_string += "        case " + selector + ":\n"
                cases_string += "            return 0;\n"
            else:
                if len(case) > 3:
                    description = case[3]
                else:
                    description = ""

                if "TPM_ALG_" in description:
                    cases_string += "#ifdef    " + description + "\n"

                cases_string += "        case " + selector + ":\n"
                cases_string += MarshalTemplates.return_type_marshal.safe_substitute(TO_TYPE=tpm_type,
                                                                                     MEMBER=parameter,
                                                                                     TO_MEMBER="")
                if "TPM_ALG_" in description:
                    cases_string += "#endif // " + description + "\n"

        cases_string = cases_string[:-1]

        template = MarshalTemplates.TYPE_Marshal_union

        code = template.safe_substitute(TYPE=mrshl_type,
                                        CASES=cases_string,
                                        ALGS=algs_string)

        return code
    # end of method - create_marshal_code(self, mrshl_type, rows, tpm_alg_ids, function_prototypes_with_flag):

    # Generate unmarshal function prototype for an entry of a UnionTable
    # Parameters:
    # mrshl_type - unmarshal function type
    # Returns:
    # generated source code
    def create_unmarshal_fp(self, mrshl_type):
        template = MarshalTemplates.TYPE_Unmarshal_union_fp
        code = template.safe_substitute(TYPE=mrshl_type)
        return code

    # Generate marshal function prototype for an entry of a UnionTable
    # Parameters:
    # mrshl_type - marshal function type
    # Returns:
    # generated source code
    def create_marshal_fp(self, mrshl_type):
        template = MarshalTemplates.TYPE_Marshal_union_fp
        code = template.safe_substitute(TYPE=mrshl_type)
        return code
