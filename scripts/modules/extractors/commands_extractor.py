# -*- coding: utf-8 -*-

import settings


class CommandsExtractor:
    """
    """
    
    def __init__(self):
        self.functions = []

    # Extracts commands from given folder
    # Parameters:
    # commands
    # folders
    # Returns:
    # list of functions
    @staticmethod
    def extract(commands, folders):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_part3_commands_pdf import CommandsExtractorPDF

            commands_extractor = CommandsExtractorPDF()
            return commands_extractor.extract_pdf(commands, folders)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_part3_commands_fodt import CommandsExtractorFODT

            commands_extractor = CommandsExtractorFODT()
            return commands_extractor.extract_fodt(commands, folders)


