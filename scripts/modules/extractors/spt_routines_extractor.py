# -*- coding: utf-8 -*-

import settings


class SupportRoutinesExtractor:
    """
    """

    def __init__(self):
        pass

    # Extracts source code of header files  from Part 4 (Spt Routines) of the specification
    # Parameters:
    # support_file - file descriptor
    # Returns:
    # string containing header file source code
    @staticmethod
    def extract_header_files(support_file, folders):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_part4_spt_routines_header_files_pdf import SptRoutinesHeaderFilesPDF

            spt_routines_extractor = SptRoutinesHeaderFilesPDF()
            return spt_routines_extractor.extract_pdf(support_file, folders)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_part4_spt_routines_header_files_fodt import SptRoutinesHeaderFilesFODT

            spt_routines_extractor = SptRoutinesHeaderFilesFODT()
            return spt_routines_extractor.extract_fodt(support_file, folders)

    # Extracts source code of the support routines from Part 4 (Spt Routines) of the specification
    # Parameters:
    # support_file - file descriptor
    # Returns:
    # string containing support routine source code
    @staticmethod
    def extract_spt_routines(support_file, folders):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_part4_spt_routines_pdf import SptRoutinesPDF

            spt_routines_extractor = SptRoutinesPDF()
            return spt_routines_extractor.extract_pdf(support_file, folders)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_part4_spt_routines_fodt import SptRoutinesFODT

            spt_routines_extractor = SptRoutinesFODT()
            return spt_routines_extractor.extract_fodt(support_file, folders)

    # Extracts source code from the annex of Part 4 (Spt Routines) of the specification
    # Parameters:
    # support_file - file descriptor
    # Returns:
    # string containing source code from the annex
    @staticmethod
    def extract_annex(support_file, folders):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_part4_spt_routines_annex_pdf import SptRoutinesAnnexPDF

            spt_routines_extractor = SptRoutinesAnnexPDF()
            return spt_routines_extractor.extract_pdf(support_file, folders)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_part4_spt_routines_annex_fodt import SptRoutinesAnnexFODT

            spt_routines_extractor = SptRoutinesAnnexFODT()
            return spt_routines_extractor.extract_fodt(support_file, folders)
