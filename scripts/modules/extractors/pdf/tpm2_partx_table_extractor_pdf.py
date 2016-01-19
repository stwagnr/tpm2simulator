# -*- coding: utf-8 -*-

import re

from modules.extractors.table_extractor import TableExtractor
from modules.data_structures import TPM2_Partx_Table
from modules import data_structures


class TableExtractorPDF(TableExtractor):
    """
    """

    # Fixes broken row
    # Parameters:
    # line - row to fix
    # offsets -  list of indexes in the line, at which the cells begin
    # columns
    # columns_content
    # Returns:
    # same row, with fixed cells
    def fix_row(self, line, offsets, columns, columns_content):
        fixed_row = range(0, columns)
        for col in fixed_row:
            fixed_row[fixed_row.index(col)] = ""

        for col in columns_content:
            pos = line.find(col)
            if pos in offsets:
                fixed_row[offsets.index(pos)] = col
            else:
                return columns_content

        return fixed_row

    # Splits a row into its cells
    # Parameters:
    # line - the row to split
    # offsets - list of indexes in the line, at which the cells begin
    # Returns:
    # list of strings with information from cells
    def split_row(self, line, offsets):
        start = 0
        res = []
        line += 100*" "
        offset_list = list(offsets)
        for o in offset_list[1:]:
            if "  " not in line and "#" not in line:
                return None
            res.append(line[start:o].strip())
            start = o
        res.append(line[start:].strip())
        return res

    # Checks if a line can belong to a table
    # Parameters:
    # file
    # line
    # table_idx - index of table to associate line with
    # header - header line of table
    # number_of_columns
    # offsets - list of indexes at which cells should begin
    # Returns:
    # probability that line is part of table
    def evaluate_line(self, file, line, table_idx, header, number_of_columns, offsets):
        num_cols = 0

        pattern = "(Table\s{1,}" + str(table_idx+1) + "\s{1,}--)"
        res = re.search(pattern, line)
        if res:
            file.seek(file.tell() - len(line))
            return 0.0

        columns_content = re.split("[ ]{2,}", line)

        if header == columns_content:
            return 1.0

        for col in columns_content:
            start = 0
            while line.find(col, start) != -1:
                o = line.find(col, start)
                if o in offsets:
                    num_cols += 1
                    break
                else:
                    start = o +1

        result = float(num_cols)/float(number_of_columns)

        if len(columns_content) - number_of_columns > 3:
            result -= 0.5

        if ("SET" in line and "(1)" in line) or ("CLEAR" in line and "(0)" in line):
            result += 1.0  # might be more than 1.0 in total at this point

        if line.startswith("#"):
            result += 0.2
            return result
        elif "+" in line:
            result += 0.2
            return result

        columns_content = self.split_row(line, offsets)
        if not columns_content:
            return 0.0
        elif result <= 0.5 and columns_content[0] == "":
            result += 0.5

        pattern = "^\d+\.\d+\.*\d*\.*\d*[ ]{1,}[A-Z]"  # e.g.: "5.3   Miscellaneous Types"
        res = re.search(pattern, line)
        if res:
            return 0.0

        pattern = "^\d+\.*\d*\.*\d*\.*\d*[ ]{1,}[A-Z]"  # e.g. "6    Constants"
        res = re.search(pattern, line)
        if res and header[0] is not "Bit" and result <= 0.5:
            return 0.0
        elif res and "Bit" not in header[0] and result < 1.0:
            result -= 0.80

        if "  " in columns_content[0] and len(columns_content[0]) < offsets[1]:
            result -= 0.5

        s = line[offsets[1]-3:offsets[1]-1]
        if s != "  ":
            result -= 0.1

        return min(result, 1.0)

    # Finds table in file, and extracts its name
    # Parameters:
    # file
    # table_idx - index of table to look for
    # Returns:
    # string with name of table
    def get_table_name(self, file, table_idx):
        pattern_table_idx = "Table[ ]+" + str(table_idx) + "[ ]+--"
        pattern_table_short_name = "[^x][ ]*(Definition [^,\n<]*?[A-Za-z]( \(.*?\))* [A_Z_]*?[^().,]*?)"
        pattern_braces = "[ ]*(\(.*?\))*"  # optional " (Actions)"
        pattern_config = "[ ]*(<.*?>)*"    # optional "<IN/OUT, S>"
        pattern = "(" + pattern_table_idx + pattern_table_short_name + pattern_braces + pattern_config + ")\n"
        result = re.search(pattern, file)
        if not result:
            return None, None
        table_name = result.group(1).strip()
        table_short_name = result.group(2).strip()

        file.seek(result.end())  # go to begin of table
        return table_name, table_short_name

    # Get list of offsets, knowing the content of every column from a line
    # Parameters:
    # line
    # column_content - list of strings with information from cells
    # Returns:
    # list of offsets of columns
    def get_offsets(self, line, columns_content):
        offsets = []
        for col in columns_content:
            offsets.append(line.find(col))
        return sorted(offsets)

    # Finds table in file, and extracts its header
    # Parameters:
    # file
    # table_name - name of table to look for
    # Returns:
    # string with header of table
    def get_table_header(self, file, table_name):

        fst_header_line = file.readline()[:-1]  # skip empty line
        fst_header_line = file.readline()[:-1]  # read first line of table
        scd_header_line = None  # there might be a second header line

        columns_content = re.split("[ ]{2,}", fst_header_line)
        fst_columns_content = columns_content
        offsets = self.get_offsets(fst_header_line, columns_content)

        scd_columns_content = None
        if columns_content and columns_content[0] == "":  # header is in more than one row
            scd_header_line = file.readline()  # skip empty line
            scd_header_line = file.readline()[:-1]  # read second header line
            columns_content = re.split("[ ]{2,}", scd_header_line)
            scd_columns_content = columns_content
            scd_offsets = self.get_offsets(scd_header_line, scd_columns_content)
            offsets = list(set(offsets) | set(scd_offsets))
            offsets = sorted(offsets)

        start = 0
        if scd_columns_content:  # get the header content (put together)
            columns_content = []
            for o in offsets[1:]:
                columns_content.append((fst_header_line[start:o] + " " + scd_header_line[start:o]).strip())
                start = o
            columns_content.append((fst_header_line[start:] + " " + scd_header_line[start:]).strip())

        return columns_content, offsets, fst_columns_content, scd_columns_content
        # finished extracting header

    # Verify if the rows has a given number of columns
    # Parameters:
    # rows
    # number of columns
    def verify_rows(self, rows, number_of_colmns):
        result = True
        for row in rows:
            if len(row) != number_of_colmns:
                result |= False
        return result

    # Extract all tables from a text file
    # Parameters:
    # file
    # Returns:
    # list of all tables from the file
    def find_all_tables(self, file):

        tables = []  # list of tables (= result of this function)
        table_idx = 1

        file_size = file.size()

        while True:  # for each table

            number_of_columns = 1
            rows = []

            # find table name
            table_name, table_short_name = self.get_table_name(file, table_idx)
            if table_name is None:
                table_idx += 1
                continue

            header, offsets, fst_columns_content, scd_columns_content = self.get_table_header(file, table_name)
            number_of_columns = len(offsets)
            number_of_columns_for_verification = number_of_columns

            while True:  # go through lines of the table (not the header)
                line = file.readline()[:-1]

                if line == "":
                    continue

                # end of page, either break, or calculate new offsets
                if line.startswith("Page") or line.startswith("Family"):
                    for i in range(0, 5):
                        line = file.readline()[:-1]
                    if file.tell() == file_size:  # end of file
                        break
                    file.seek(file.tell() - len(line) - 1)

                    columns_content = re.split("[ ]{2,}", line)
                    if fst_columns_content == columns_content:
                        file.seek(file.tell() - 1)
                        header, offsets, fst_columns_content, scd_columns_content = self.get_table_header(file, table_name)

                    continue

                probability = self.evaluate_line(file, line, table_idx, header, number_of_columns, offsets)
                if probability < 0.25:
                    break

                if number_of_columns != 1 and len(rows) <= 1 and not "NOTE" in line:
                    columns_content = re.split("[ ]{2,}", line)
                    if len(columns_content) != number_of_columns:
                        columns_content = self.split_row(line, offsets)
                else:
                    columns_content = self.split_row(line, offsets)
                    if not columns_content:
                        break

                if rows and columns_content[0] == "" and not columns_content[1].startswith("#"):
                    for i in range(1, number_of_columns):
                        if columns_content[i] is not "":
                            rows[len(rows)-1][i] += " "
                        rows[len(rows)-1][i] += columns_content[i]
                else:
                    l = []
                    for e in list(columns_content):
                        l.append(e.strip())
                    rows.append(l)

                # print "{:1.2f}: {:s}".format(probability, line)

            if not self.verify_rows(rows, number_of_columns_for_verification):
                raise AssertionError("Wrong number of columns in row of Table " + table_idx)

            regex_multiple_spaces = re.compile(r"\s{2,}")
            table_name = regex_multiple_spaces.sub(" ", table_name)
            table_short_name = regex_multiple_spaces.sub(" ", table_short_name)

            pattern = "([^<]*)"
            result = re.search(pattern, table_short_name)
            table_short_name = result.group(1).strip()
            table_short_name = re.sub('\([^)]*\)\s*$', "", table_short_name)
            table_short_name = re.sub('\s*$', "", table_short_name)

            table = TPM2_Partx_Table(table_name, table_short_name, str(table_idx), rows)

            name = table_short_name
            table = self.classify_table(table, name)

            print table_name
            tables.append(table)

            if file.tell() == file_size:  # end of file
                break

            table_idx += 1

        return tables

    # Main function to call from this class
    # Parameters:
    # file
    # Returns list of internal representation of tables in file
    def extract_structure_tables_pdf(self, file):
        return self.find_all_tables(file)
    # end of method - extract_tables(xml):

    # Extracts command with specified name
    # Parameters:
    # file
    # command_short_name
    # Returns:
    # command table with given name
    def extract_commands_table_command_pdf(self, file, command_short_name):
        in_table = None
        table_found = False

        result = re.search('TPM2_(' + command_short_name + ') Command\n', file)
        if result is not None:
            file.seek(result.end())
        else:
            return

        while True:
            line = file.readline()[:-1]
            if line == "":
                continue

            if "Table" in line or "Page" in line:
                break

            result = re.search("([ ]*Type[ ]+Name[ ]+Description.*)", line)
            if result:
                table_found = True
                row = result.group(1)+"\n"
                results = re.split("[ ]{5,}", row)
                offsets = []
                l = []
                for r in results:
                    r = r.strip()
                    l.append(r)
                    offsets.append(line.find(r))
                in_table = data_structures.TPM2_Partx_Table(command_short_name, command_short_name, None, [l])
            elif table_found:
                row = line + "\n"
                row = self.split_row(row, offsets)
                if row[0] is "":
                    continue
                in_table.rows.append(row)

        return in_table

    # Extracts response with specified name
    # Parameters:
    # file
    # short_name - short name of response
    # Returns:
    # response table with given name
    def extract_commands_table_response_pdf(self, file, short_name):
        out_table = None
        table_found = False
        while True:
            line = file.readline()[:-1]
            if line == "":
                continue

            if "Table" in line or "Page" in line:
                break

            result2 = re.search("([ ]*Type[ ]+Name[ ]+Description.*)", line)
            if result2:
                table_found = True
                row = result2.group(1)+"\n"
                results = re.split("[ ]{5,}", row)
                offsets = []
                l = []
                for r in results:
                    r = r.strip()
                    l.append(r)
                    offsets.append(line.find(r))
                out_table = data_structures.TPM2_Partx_Table(short_name, short_name, None, [l])
            elif table_found:
                row = line + "\n"
                row = self.split_row(row, offsets)
                if row[0] is "":
                    continue
                out_table.rows.append(row)
        return out_table