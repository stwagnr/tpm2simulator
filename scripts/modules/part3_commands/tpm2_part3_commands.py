# -*- coding: utf-8 -*-

from modules.extractors.commands_extractor import CommandsExtractor

from modules.part3_commands.tpm2_part3_commands_prototypes import CommandPrototypeFile as PrototypeFile
from modules.part3_commands.tpm2_part3_commands_h import CommandsHeaderFile
from modules.part3_commands.tpm2_part3_command_attributes_h import CommandAttributesHeaderFile
from modules.part3_commands.tpm2_part3_handle_process import HandleProcess
from modules.part3_commands.tpm2_part3_command_dispatcher import CommandDispatcher

from modules import constants
from modules.file_handling import FileHandling
from modules.extractors.license_extractor import LicenseExtractor

import settings


class Commands:
    """
    """

    def __init__(self):
        self.command_header_file = CommandsHeaderFile()

        self.command_dispatcher = CommandDispatcher()

        if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
            from modules.part3_commands.tpm2_part3_command_dispatch_data import CommandDispatchData
            self.command_dispatch_data = CommandDispatchData()

        self.list_of_tables_commands = []

        self.COMMAND_PATH = constants.SRC_PATH + constants.TPM_PATH + "command/"

        self.current_section = ""

    # Creates HandleProcess.c file
    def create_handle_process(self):
        print ""
        print "Creating HandleProcess.c"
        p = HandleProcess()
        for command in self.list_of_tables_commands:
            print "    * " + command.name
            p.create_handle_process_case_pdf(command.name, command.rows)
        p.write()

    # Handles commands
    # Parameter:
    # commands
    def handle_commands(self, commands):

        for command in commands:

            if command.table_command is not None:
                self.list_of_tables_commands.append(command.table_command)

            ###################################################################
            # PROTOTYPES (START)
            prototype_file = PrototypeFile(command.short_name)
            prototype_file.extract_structures_and_modifiers(command.short_name,
                                                            command.table_command,
                                                            command.table_response,
                                                            self.command_dispatcher)
            prototype_file.extract_prototype_functions(command)
            prototype_file.write()
            # PROTOTYPES (END)
            ###################################################################

            file_content = command.elements_to_string()

            file_path = self.COMMAND_PATH + command.folder_name + "/" + command.file_name

            # correct file path for EC_Ephemeral.c
            if "EC_Ephemeral.c" in command.file_name:
                file_path = self.COMMAND_PATH + "Asymmetric/" + command.file_name

            FileHandling.write_file(file_path, file_content)

            # add prototype header file to Commands.h
            if command.name.startswith("TPM2_"):
                if command.section_name != self.current_section:
                    self.command_header_file.append("\n\n")
                    self.command_header_file.append("// " + command.section_name + "\n")
                    self.current_section = command.section_name
                self.command_header_file.append("#include     \"" + command.short_name + "_fp.h\"\n")

        self.command_header_file.write()

        self.command_dispatcher.write()

        if settings.ENABLE_TABLE_DRIVEN_DISPATCHER:
            self.command_dispatch_data.write()

        # create HandleProcess.c
        if settings.SPEC_VERSION_INT < 138:
            self.create_handle_process()

    # Extracts information from commands file
    # Parameters:
    # commands_file
    # folders
    def extract(self, commands_file, folders):
        # extract license text
        license_text = LicenseExtractor.extract_license(commands_file)
        FileHandling.set_license(license_text)

        # extract CommandAttributes.h
        self.command_attributes_header_file = CommandAttributesHeaderFile()
        self.command_attributes_header_file.write()

        commands = CommandsExtractor.extract(commands_file, folders)
        self.handle_commands(commands)




