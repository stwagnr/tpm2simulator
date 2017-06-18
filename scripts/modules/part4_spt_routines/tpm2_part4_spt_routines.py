# -*- coding: utf-8 -*-

from modules.extractors.spt_routines_extractor import SupportRoutinesExtractor
from modules.part4_spt_routines.tpm2_part4_spt_routines_prototypes import SupportRoutinesPrototypeFile as PrototypeFile
from modules.extractors.fodt.tpm2_partx_extraction_navigator_fodt import ExtractionNavigator
from modules import constants
from modules.file_handling import FileHandling
from modules.extractors.license_extractor import LicenseExtractor
import settings

class SptRoutines(ExtractionNavigator):
    """
    """

    # Creates appropriate file path for given filename
    # Parameters:
    # name_folder
    # name - name of the file
    # Returns:
    # file path of the given file name
    def set_file_path(self, name_folder, name):
        if name_folder is None:
            name_folder = "subsystem/"

        if "CommandAttributeData.c" in name:
            file_path = constants.SRC_PATH + constants.TPM_PATH + "include/" + name
        elif "Attest_spt.c" in name:
            file_path = self.COMMAND_PATH + "Attestation/" + name
        elif "Context_spt.c" in name:
            file_path = self.COMMAND_PATH + "Context/" + name
        elif "NV_spt.c" in name:
            file_path = self.COMMAND_PATH + "NVStorage/" + name
        elif "Object_spt.c" in name:
            file_path = self.COMMAND_PATH + "Object/" + name
        elif "Policy_spt.c" in name:
            file_path = self.COMMAND_PATH + "EA/" + name
        elif "EncryptDecrypt_spt.c" in name:
            file_path = self.COMMAND_PATH + "Symmetric/" + name
        elif "HandleProcess_fp.h" in name:
            file_path = constants.SRC_PATH + constants.TPM_PATH + "include/prototypes/" + name
        elif "CommandDispatcher_fp.h" in name:
            file_path = constants.SRC_PATH + constants.TPM_PATH + "include/prototypes/" + name
        else:
            file_path = constants.SRC_PATH + constants.TPM_PATH + name_folder + "/" + name

        return file_path

    # Handles support routines
    # Parameters:
    # spt_routines - list of support routines
    def handle_support_routines(self, spt_routines):

        for spt_routine in spt_routines:

            # create the prototype file if it needs to be created
            if spt_routine.name.endswith(".c"):
                prototype_file = PrototypeFile(spt_routine.short_name)
                prototype_file.extract_prototype_functions(spt_routine)

                if settings.SPEC_VERSION_INT >= 138 and "ExecuteCommand" in spt_routine.short_name:
                    prototype_file.file_path = prototype_file.file_path.replace("ExecuteCommand", "ExecCommand")
                prototype_file.write()

            file_content = spt_routine.elements_to_string()

            # Set file path
            file_path = self.set_file_path(spt_routine.folder_name, spt_routine.file_name)

            if settings.SPEC_VERSION_INT >= 138 and spt_routine.name.endswith(".h"):
                file_path = constants.SRC_PATH + constants.TPM_PATH + "include/" + spt_routine.file_name

            # Write file
            FileHandling.write_file(file_path, file_content)

    # Extracts and handles information from part 4 of the specification and generates appropriate code
    # Parameters:
    # support_file
    # dict_sections_spt_routines_header_files
    def extract(self, support_file, dict_sections_spt_routines_header_files):
        # extract license text
        license_text = LicenseExtractor.extract_license(support_file)
        FileHandling.set_license(license_text)

        spt_routines = SupportRoutinesExtractor.extract_spt_routines(support_file, dict_sections_spt_routines_header_files)
        self.handle_support_routines(spt_routines)

        return None
    # end of method - extract(self, xml):
