# -*- coding: utf-8 -*-

import settings


# Class contains methods to extract tables from any part of the specification
class TableExtractor(object):
    """
    """

    def __init__(self):
        pass

    # Extracts all the tables from Part 2 (Structures) of the specification in either text or xml format
    # Parameters:
    # structures_file - file descriptor
    # Returns:
    # list of internal representations of all tables
    @staticmethod
    def extract_structure_tables(structures_file):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_partx_table_extractor_pdf import TableExtractorPDF

            table_extractor = TableExtractorPDF()
            return table_extractor.extract_structure_tables_pdf(structures_file)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_partx_table_extractor_fodt import TableExtractorFODT

            table_extractor = TableExtractorFODT()
            return table_extractor.extract_structure_tables_fodt(structures_file)

    # Extracts command table with given name from Part 3 (Commands) of the specification in either text or xml format
    # Parameters:
    # commands_file - file descriptor
    # Returns:
    # command table with given name
    @staticmethod
    def extract_commands_table_command(commands_file, command_short_name):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_partx_table_extractor_pdf import TableExtractorPDF

            table_extractor = TableExtractorPDF()
            return table_extractor.extract_commands_table_command_pdf(commands_file, command_short_name)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_partx_table_extractor_fodt import TableExtractorFODT

            table_extractor = TableExtractorFODT()
            return table_extractor.extract_commands_table_command_fodt(commands_file, command_short_name)

    # Extracts response table with given name from Part 3 (Commands) of the specification in either text or xml format
    # Parameters:
    # commands_file - file descriptor
    # Returns:
    # response table with given name
    @staticmethod
    def extract_commands_table_response(commands_file, command_short_name):
        if settings.DATA_ORIGIN_PDF_TXT:
            # deferred import
            from modules.extractors.pdf.tpm2_partx_table_extractor_pdf import TableExtractorPDF

            table_extractor = TableExtractorPDF()
            return table_extractor.extract_commands_table_response_pdf(commands_file, command_short_name)

        else:
            # deferred import
            from modules.extractors.fodt.tpm2_partx_table_extractor_fodt import TableExtractorFODT

            table_extractor = TableExtractorFODT()
            return table_extractor.extract_commands_table_response_fodt(commands_file, command_short_name)

    # Finds out table type from its name
    # Parameters:
    # table - internal representation of table to be classified
    # name - name of the table
    # Returns:
    # same table, with type correctly set
    @staticmethod
    def classify_table(table, name):
        if name.startswith("Definition") and name.endswith("Constants"):
            table.table_type = "EnumTable"

        elif name.startswith("Definition") and name.endswith("Values"):
            table.table_type = "EnumTable"

        elif name.startswith("Definition of") and "Types" in name:
            table.table_type = "TypedefTable"

        elif name.startswith("Definition") and name.endswith("Type"):
            table.table_type = "InterfaceTable"

        elif name.startswith("Definition") and name.endswith("Structure"):
            table.table_type = "StructureTable"

        elif name.startswith("Definition") and name.endswith("Bits"):
            table.table_type = "BitsTable"

        elif name.startswith("Definition") and name.endswith("Union"):
            table.table_type = "UnionTable"

        return table
