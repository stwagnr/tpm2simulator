# -*- coding: utf-8 -*-

import re

from modules.extractors.table_extractor import TableExtractor
from modules.data_structures import TPM2_Partx_Table
from modules import constants


class TableExtractorFODT(TableExtractor):
    """
    """
    # Extract all tables from Part 2 of the specification given as a .fodt file
    # Parameters:
    # xml - opened xml file
    # Returns:
    # list of all tables from the file
    def extract_structure_tables_fodt(self, xml):
        tables = xml.find_all(constants.XML_TABLE_TABLE)
        table_names = []
        tables_to_remove = []

        for table in tables:
            text_p = table.find_previous(constants.XML_TEXT_P)
            text_p_text = text_p.get_text()
            while not "Table" in text_p_text:
                text_p = text_p.find_previous(constants.XML_TEXT_P)
                text_p_text = text_p.get_text()
                if table_names and table_names[-1] == text_p_text:
                    text_p_text = "Table xx"  # skip this table, which is actually a figure

            name = text_p_text

            if "Table" not in name:
                tables_to_remove.append(table)
            elif 'Table xx' in name or 'Table A' in name:
                tables_to_remove.append(table)
            else:
                table_names.append(name)
        # end of loop - for table in tables:

        for table in tables_to_remove:
            tables.remove(table)

        returned_tables = []
        for idx, table in enumerate(tables):
            rows = []
            # name = table['table:name']
            table_rows = table.find_all(constants.XML_TABLE_TABLE_ROW)
            for row in table_rows[1:]:  # skip row with column names
                cells = row.find_all(constants.XML_TABLE_TABLE_CELL)
                if len(cells) is 2:
                    value = cells[0].get_text().replace('\n', '').strip()
                    comment = cells[1].get_text().replace('\n', '').strip()
                    rows.append([value, comment])

                elif len(cells) is 3:  # TYPES AND STRUCTURES
                    var_type = cells[0].get_text().replace('\n', '').strip()
                    name = cells[1].get_text().replace('\n', '').strip()
                    desc = cells[2].get_text().replace('\n', '').strip()
                    rows.append([var_type, name, desc])

                elif len(cells) is 4:  # UNION
                    parameter = cells[0].get_text().replace('\n', '').strip()
                    var_type = cells[1].get_text().replace('\n', '').strip()
                    selector = cells[2].get_text().replace('\n', '').strip()
                    desc = cells[3].get_text().replace('\n', '').strip()
                    rows.append([parameter, var_type, selector, desc])

                elif len(cells) is 7:  # TPM_ALG_ID
                    algorithm_name = cells[0].get_text().replace('\n', '').strip()
                    value = cells[1].get_text().replace('\n', '').strip()
                    var_type = cells[2].get_text().replace('\n', '').strip()
                    dep = cells[3].get_text().replace('\n', '').strip()
                    c = cells[4].get_text().replace('\n', '').strip()
                    reference = cells[5].get_text().replace('\n', '').strip()
                    comments = cells[6].get_text().replace('\n', '').strip()
                    rows.append([algorithm_name, value, var_type, dep, c, reference, comments])
            # end of loop - for row in table_rows[1:]:

            result = re.search(u'— ([^<]*)', table_names[idx])
            if result is None:
                continue

            name = result.group(1)
            name = re.sub('\([^)]*\)\s*$', "", name)
            name = re.sub('\s*$', "", name)

            result = re.search(u'Table ([0-9]*)', table_names[idx])
            number = result.group(1)

            table_inst = TPM2_Partx_Table(table_names[idx], name, number, rows)

            table_inst = self.classify_table(table_inst, name)

            # print str(d.number) + ": " + str(d.table_type)
            returned_tables.append(table_inst)
        # end of loop - for idx, table in enumerate(tables)

        return returned_tables
    # end of method - extract_tables(xml):

    # Extracts command with specified name
    # Parameters:
    # xml -opened xml file
    # short_name - command short name
    # Returns:
    # command table with given name
    def extract_commands_table_command_fodt(self, xml, short_name):
        name = ""

        if "_TPM" in short_name:
            return None

        t = xml.find_next(constants.XML_TABLE_TABLE)
        while True:
            name = ""
            s = None
            for sibling in t.previous_sibling.previous_sibling:
                if type(sibling) is unicode:
                    s = sibling
                    name += sibling
                else:
                    if sibling.string:
                        if '\n' or '\r' in sibling.string:
                            s = sibling.string
                        name += s
                    if sibling.string is None:
                        name += sibling.get_text()

            if short_name in name and name.endswith("Command"):
                break

            t = t.find_next(constants.XML_TABLE_TABLE)

        table = t
        table_name = name
        # end of loop - for table in tables:

        rows = []
        # name = table['table:name']
        table_rows = table.find_all(constants.XML_TABLE_TABLE_ROW)
        for row in table_rows:
            cells = row.find_all(constants.XML_TABLE_TABLE_CELL)
            var_type = cells[0].get_text().replace('\n', '').strip()
            name = cells[1].get_text().replace('\n', '').strip()
            desc = cells[2].get_text().replace('\n', '').strip()
            rows.append([var_type, name, desc])
        # end of loop - for row in table_rows[1:]:

        result = re.search(u'— ([^<]*)', table_name)
        name = result.group(1)
        name = re.sub('\([^)]*\)\s*$', "", name)
        name = re.sub('\s*$', "", name)

        result = re.search(u'Table ([0-9]*)', table_name)
        number = result.group(1)

        table_inst = TPM2_Partx_Table(short_name, short_name, number, rows)
        table_inst.table_type = "CommandTable"

        return table_inst
    # end of method - extract_commands_table_command_fodt:

    # Extracts response with specified name
    # Parameters:
    # xml - opened xml file
    # short_name - short name of response
    # Returns:
    # response table with given name
    def extract_commands_table_response_fodt(self, xml, short_name):
        name = ""

        if "_TPM" in short_name:
            return None

        t = xml.find_next(constants.XML_TABLE_TABLE)
        while True:
            name = ""
            s = None
            for sibling in t.previous_sibling.previous_sibling:
                if type(sibling) is unicode:
                    s = sibling
                    name += sibling
                else:
                    if sibling.string:
                        if '\n' or '\r' in sibling.string:
                            s = sibling.string
                        name += s
                    if sibling.string is None:
                        name += sibling.get_text()

            if short_name in name and name.endswith("Response"):
                break

            t = t.find_next(constants.XML_TABLE_TABLE)

        table = t
        table_name = name

        rows = []
        # name = table['table:name']
        table_rows = table.find_all(constants.XML_TABLE_TABLE_ROW)
        for row in table_rows:
            cells = row.find_all(constants.XML_TABLE_TABLE_CELL)
            var_type = cells[0].get_text().replace('\n', '').strip()
            name = cells[1].get_text().replace('\n', '').strip()
            desc = cells[2].get_text().replace('\n', '').strip()
            rows.append([var_type, name, desc])
        # end of loop - for row in table_rows[1:]:

        result = re.search(u'— ([^<]*)', table_name)
        name = result.group(1)
        name = re.sub('\([^)]*\)\s*$', "", name)
        name = re.sub('\s*$', "", name)

        result = re.search(u'Table ([0-9]*)', table_name)
        number = result.group(1)

        table_inst = TPM2_Partx_Table(short_name, short_name, number, rows)
        table_inst.table_type = "ResponseTable"

        return table_inst
