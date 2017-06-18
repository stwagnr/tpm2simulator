# -*- coding: utf-8 -*-
import re

from modules.extractors.spt_routines_extractor import SupportRoutinesExtractor
from tpm2_part4_spt_routines_prototypes import SupportRoutinesPrototypeFile as PrototypeFile
from modules import constants
from modules.file_handling import FileHandling
from modules.extractors.license_extractor import LicenseExtractor
import settings

class SptRoutinesAnnex:
    """
    """

    def __init__(self):
        pass

    # Creates appropriate file path for given filename
    # Parameters:
    # name_folder
    # name - name of the file
    # Returns:
    # file path of the given file name
    def set_file_path(self, name_folder, name):
        if ((name.endswith(".h") and not
                (name.startswith("Implementation") or
                name.startswith("TpmTcpProtocol") or
                name.startswith("OsslCryptoEngine")))
                or "CpriDataEcc.c" in name
                or "CpriHashData.c" in name):
            file_path = constants.SRC_PATH + constants.TPM_PATH + "../include/" + name
        else:
            file_path = constants.SRC_PATH + constants.TPM_PATH + name_folder + "/" + name
        return file_path

    # Handles functions from the annex part of part 4 of the specification
    # Parameters:
    # functions - list of functions
    def handle_annex(self, functions):

        if settings.SPEC_VERSION_INT >= 138:
            prototype_file_simulator = PrototypeFile("Simulator")
            prototype_file_simulator.file_path = constants.SRC_PATH + "simulator/include/prototypes/Simulator_fp.h"

        for function in functions:

            ###################################################################
            # PROTOTYPES (START): check if proto files needs to be created
            if "../OsslCryptoEngine" in function.folder_name and function.name.endswith(".c"):
                prototype_file = PrototypeFile(function.short_name)
                prototype_file.extract_prototype_functions(function)
                prototype_file.write()

            if settings.SPEC_VERSION_INT >= 138 and "../simulator" in function.folder_name and function.name.endswith(".c"):
                prototype_file_simulator.extract_prototype_functions(function)
            # PROTOTYPES (END)
            ###################################################################

            file_content = function.elements_to_string()

            if function.name.strip().endswith("()"):
                function.name = function.name.strip().replace("()", "_fp.h")
            elif function.name.strip().endswith(")"):
                result = re.search('\((.*)\)', function.name.strip())
                if result:
                    function.name = result.group(1)

            # FIX for CpriHashData.c
            if "CpriHashData.c" in function.name:
                file_content = file_content.replace("#ifdef", "#ifdef ")
            #

            file_path = self.set_file_path(function.folder_name, function.name)

            if settings.SPEC_VERSION_INT >= 138:
                if "PlatformData.h" in function.name:
                    file_path = constants.SRC_PATH + "platform/include/" + function.name
                if "Platform_fp.h" in function.name:
                    file_path = constants.SRC_PATH + "platform/include/prototypes/" + function.name

                if "TpmTcpProtocol.h" in function.name:
                    file_path = constants.SRC_PATH + "simulator/include/" + function.name

                if "TpmToOssl" in function.name and function.name.endswith(".h"):
                    file_path = constants.SRC_PATH + "tpm/include/ossl/" + function.name

            FileHandling.write_file(file_path, file_content)

        if settings.SPEC_VERSION_INT >= 138:
            prototype_file_simulator.write()

    # Extracts and handles information from the annex part of part 4 of the specification and generates appropriate code
    # Parameters:
    # support_file
    # dict_sections_spt_routines_header_files
    def extract(self, support_file, dict_sections_spt_routines_header_files):
        # extract license text
        license_text = LicenseExtractor.extract_license(support_file)
        FileHandling.set_license(license_text)

        spt_routines_annex = SupportRoutinesExtractor.extract_annex(support_file, dict_sections_spt_routines_header_files)
        self.handle_annex(spt_routines_annex)

        return None
    # end of method - extract(...):
