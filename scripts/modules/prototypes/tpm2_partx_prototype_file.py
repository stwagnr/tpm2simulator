# -*- coding: utf-8 -*-

from modules import constants
from modules.prototypes.tpm2_partx_prototype_functions import PrototypeFunctions
from modules.prototypes.tpm2_partx_prototype_component import PrototypeComponent as PrototypeStructure
from modules.prototypes.tpm2_partx_prototype_modifiers import PrototypeModifiers


class PrototypeFile:

    # Initializes prototype file object
    def __init__(self, name):
        if name is None or name is "":
            raise AssertionError
        self.name = name

        if self.name.startswith("Cpri") or self.name.startswith("MathFunctions") or self.name.startswith("RSAKeySieve"):
            self.file_path = constants.SRC_PATH + "include/" + self.name + "_fp.h"
        else:
            self.file_path = constants.SRC_PATH + constants.TPM_PATH + "include/prototypes/" + self.name + "_fp.h"

        self.header_name = "_" + self.name + "_H_"
        self.header_name_sup = "_" + self.name.upper().replace(".", "_") + "_FP_H_"

        self.functions = PrototypeFunctions()
        self.structure_in = PrototypeStructure()
        self.structure_out = PrototypeStructure()
        self.modifiers = PrototypeModifiers()

        self.file = None  # the output file handle

    # Function is not implemented
    def extract_prototype_functions(self, text_p_text):
        raise NotImplementedError

    # Function is not implemented
    def write(self):
        raise NotImplementedError
