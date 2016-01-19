# -*- coding: utf-8 -*-

from modules.prototypes.tpm2_partx_prototype_component import PrototypeComponent


class PrototypeModifiers(PrototypeComponent):

    # Initializes object
    def __init__(self):
        PrototypeComponent.__init__(self)
        self.content = u''
        self.modifier_number = 1
        self.in_handle_section = True

    # Adds modifier handle
    # Parameters:
    # name
    # new_type
    def add_modifier_handle(self, name, new_type):
        self.append("#define    RC_" + name + "_" + new_type + \
                    "\t\t(TPM_RC_H + TPM_RC_" + str(self.modifier_number) + ")\n")
        self.modifier_number += 1

    # Adds modifier handle parameter
    # Parameters:
    # name
    # new_type
    def add_modifier_param(self, name, new_type):
        if self.in_handle_section:
            self.in_handle_section = False
            self.modifier_number = 1

        self.append("#define    RC_" + name + "_" + new_type + \
                    "\t\t(TPM_RC_P + TPM_RC_" + str(self.modifier_number) + ")\n")
        self.modifier_number += 1

    # Changes section type
    def replace_section_type(self):
        self.content = self.content.replace("TPM_RC_H", "TPM_RC_P")