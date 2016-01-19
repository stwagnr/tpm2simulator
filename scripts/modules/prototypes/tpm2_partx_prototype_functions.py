# -*- coding: utf-8 -*-

from modules.prototypes.tpm2_partx_prototype_component import PrototypeComponent


class PrototypeFunctions(PrototypeComponent):

    # Initialises object
    def __init__(self):
        PrototypeComponent.__init__(self)
        self.content = u''
