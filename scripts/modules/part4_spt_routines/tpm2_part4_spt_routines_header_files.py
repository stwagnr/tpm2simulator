# -*- coding: utf-8 -*-

from modules.extractors.spt_routines_extractor import SupportRoutinesExtractor
from modules import constants
from modules.file_handling import FileHandling
from modules.extractors.license_extractor import LicenseExtractor
import settings


class SptRoutinesHeaderFiles():
    """
    """

    # Handles header files from the annex part of part 4 of the specification
    # Parameters:
    # spt_routines
    @staticmethod
    def handle_support_routines_header_files(spt_routines):

        for function in spt_routines:
            file_content = function.elements_to_string()

            #####################################################################
            # Modification based on settings
            if "TpmBuildSwitches.h" in function.name and not settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
                file_content = file_content.replace("#define TABLE_DRIVEN_DISPATCH",
                                                    "// #define TABLE_DRIVEN_DISPATCH")

            if "VendorString.h" in function.name:
                file_content = file_content.replace('// #define    MANUFACTURER    "MSFT"',
                                                  '#define   MANUFACTURER      "' + str(settings.MANUFACTURER) + '"')
                file_content = file_content.replace('// #define       VENDOR_STRING_1       "DPA "',
                                                  '#define   VENDOR_STRING_1   "' + str(settings.VENDOR_STRING_1) + '"')
                file_content = file_content.replace('// #define   FIRMWARE_V1         (0x20140711)',
                                                  '#define   FIRMWARE_V1       ' + str(settings.FIRMWARE_V1))
            #####################################################################

            file_path = constants.SRC_PATH + constants.TPM_PATH + function.folder_name + "/" + function.name

            # correct file path: save fiels to global include folder
            file_names = ["bits.h", "bool.h", "swap.h", "TpmError.h"]
            if function.name in file_names:
                file_path = constants.SRC_PATH + constants.TPM_PATH + "../include/" + function.name

            FileHandling.write_file(file_path, file_content)

    # Extracts and handles header files from part 4 of the specification and generates appropriate code
    # Parameters:
    # support_file
    # dict_sections_spt_routines_header_files
    def extract(self, support_file, dict_sections_spt_routines_header_files):
        # extract license text
        license_text = LicenseExtractor.extract_license(support_file)
        FileHandling.set_license(license_text)

        spt_routines = SupportRoutinesExtractor.extract_header_files(support_file,
                                                                     dict_sections_spt_routines_header_files)
        self.handle_support_routines_header_files(spt_routines)

        return None
    # end of method - extract(self, xml):


