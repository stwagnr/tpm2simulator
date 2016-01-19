# -*- coding: utf-8 -*-

from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules.part2_structures.marshal import tpm2_partx_marshal_templates


class BitsTableMarshaller(SimpleMarshaller):

    def __init__(self):
        SimpleMarshaller.__init__(self)

    # Generate unmarshal function for Bits tables
    # Parameters: values used to substitute fields of the template
    # Returns:
    # generated source code
    def create_unmarshal_code(self, mrshl_type, to_type, reserved, rc_fail="TPM_RC_VALUE"):

        reserved = reserved.lower()

        template = tpm2_partx_marshal_templates.TYPE_Unmarshal_bits
        code = template.safe_substitute(TYPE=mrshl_type, TO_TYPE=to_type, RESERVED=reserved, RC_FAIL=rc_fail)

        return code
