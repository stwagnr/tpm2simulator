# -*- coding: utf-8 -*-

from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules.part2_structures.marshal import tpm2_partx_marshal_templates
from textwrap import dedent


class AdvancedMarshaller(SimpleMarshaller):

    def __init__(self):
        SimpleMarshaller.__init__(self)

    # Generate unmarshal function for advanced types
    # Parameters: values used to substitute fields of the template
    # Returns:
    # generated source code
    def create_unmarshal_code(self, mrshl_type, to_type, cases_list, rc_fail="TPM_RC_VALUE"):

        cases = ""
        for case in cases_list:
            cases += "            case " + case + " :\n"

        cases = cases[12:]
        cases = cases[:-1]
        cases = dedent(cases)

        rc_fail = rc_fail.strip()

        template = tpm2_partx_marshal_templates.TYPE_Unmarshal_advanced
        code = template.safe_substitute(TYPE=mrshl_type, TO_TYPE=to_type, CASES=cases, RC_FAIL=rc_fail)

        return code
