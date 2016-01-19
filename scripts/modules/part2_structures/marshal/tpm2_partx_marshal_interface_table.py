# -*- coding: utf-8 -*-

from string import Template
from textwrap import dedent

from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules.part2_structures.marshal import tpm2_partx_marshal_templates as MarshalTemplates


class InterfaceTableMarshaller(SimpleMarshaller):

    def __init__(self):
        SimpleMarshaller.__init__(self)

    # Generate unmarshal function for InterfaceTables
    # Parameters:
    # mrshl_type, to_type - values used to substitute fields of the interface unmarshalling template
    # cases_list - list used to generate unmarshaling cases
    # alg_list, checks_list - lists used to create additional checks and conditions
    # cond, rc_fail - values used to substitute fields of interface condition template
    # Returns:
    # generated source code
    def create_unmarshal_code(self, mrshl_type, to_type, cases_list, alg_list, checks_list, cond=None, rc_fail="TPM_RC_VALUE"):

        # CASES
        cases_string = ""
        if cases_list and isinstance(cases_list[0], (int, long)):
            for case in cases_list:
                cases_string += "            case " + str(case) + ":\n"

        elif cases_list:
            for case in cases_list:
                if "TPM_ALG_" in case:
                    cases_string += MarshalTemplates.ifdef_case_template.safe_substitute(CASE=case)
                else:
                    cases_string += "            case " + case + ":\n"

        # ALGs
        algs_string = ""
        if alg_list:
            for alg in alg_list:
                alg_name = alg.name
                algs_string += MarshalTemplates.ifdef_case_template.safe_substitute(CASE=alg_name)

        #    algs_string = algs_string[:-1]

        # CHECKS
        checks_string = ""
        if checks_list:
            checks_string = "if(" + MarshalTemplates.target_bounds_check_template.safe_substitute(
                                        LEFT_BOUNDARY=checks_list[0][0], RIGHT_BOUNDARY=checks_list[0][1])

            for check in checks_list[1:]:
                checks_string += "\n" + 8 * " " + "&& " \
                                + MarshalTemplates.target_bounds_check_template.safe_substitute(
                                        LEFT_BOUNDARY=check[0], RIGHT_BOUNDARY=check[1])

            checks_string += ")\n"

        if rc_fail:
            checks_string += 12 * " " + "rc = " + rc_fail + ";\n"

        checks_string = checks_string[:-1]
        checks_string = dedent(checks_string)

        condition = ""
        if cases_list and not checks_list:
            if cond:
                condition = MarshalTemplates.interface_condition_caseif_template.safe_substitute(COND=cond, RC_FAIL=rc_fail)

            template = MarshalTemplates.TYPE_Unmarshal_interface
        elif not cases_list and checks_list:
            if cond:
                condition = MarshalTemplates.interface_condition_if_template.safe_substitute(COND=cond, RC_FAIL=rc_fail)

            template = MarshalTemplates.TYPE_Unmarshal_interface2
        else:
            if cond:
                condition = MarshalTemplates.interface_condition_caseifnot_template.safe_substitute(COND=cond, RC_FAIL=rc_fail)

            template = MarshalTemplates.TYPE_Unmarshal_interface

        flag = ""
        if cond:
            flag = ", BOOL     allowNull"

        code = template.safe_substitute(
            TYPE=mrshl_type,
            TO_TYPE=to_type,
            ALGS=algs_string + cases_string,
            CHECKS=checks_string,
            CONDITION=condition,
            FLAG=flag,
            RC_FAIL=rc_fail)

        return code
