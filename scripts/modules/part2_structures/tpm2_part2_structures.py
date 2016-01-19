# -*- coding: utf-8 -*-

import re  # regex

import modules.constants as constants
from modules.extractors.license_extractor import LicenseExtractor
from modules.part2_structures.tpm2_part2_structures_types import BaseTypes, TpmTypes
from modules.part2_structures.tpm2_part2_structures_alg_ids import AlgorithmIDs
from modules.part2_structures.marshal.tpm2_partx_marshal import Marshaller
from modules import utils
from modules.extractors.table_extractor import TableExtractor
from modules.file_handling import FileHandling


# Class which handles tables from Part 2 of the TPM Simulator specification
class Structures:

    # Initializes header file content to empty string and instantiates Marshaller class
    def __init__(self):
        self.tpm_types_h_file_content = ""
        self.marshaller = Marshaller()

    # Handles data from Typedef tables, writes type definitions and corresponding dependency
    # (if applicable to table) into the header file content, by interpreting the strings from the first column as the
    # base types, and the strings from the second column as the new types. If a new type name containg an algorithm
    # type, type definitions are created with every corresponding algorithm ID
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table to be handled
    # tmp_alg_ids - mapping from algorithm types to list of corresponding algorithm IDs
    def handle_typedef_table(self, table, tpm_alg_ids):
        table_dependence = utils.find_alg_constraints(table.short_name)
        if table_dependence:  # if table dependence {*} found in table name
            self.tpm_types_h_file_content += "#ifdef      TPM_ALG_" + table_dependence + "\n"

        for row in table.rows:
            base_type = row[0]
            name = row[1]

            # check for !ALG
            alg_ids_list = utils.expand_alg_macro(name, tpm_alg_ids, table_dependence)
            # if new type name contains algorithm type, create type definition for all corresponding IDs
            if alg_ids_list:
                for alg in alg_ids_list:
                    new_type = utils.replace_alg_placeholder(name, alg.short_name)
                    self.tpm_types_h_file_content += "typedef  " + base_type + utils.indent(base_type) + new_type + ";\n"
            else:  # else create type definition for table name
                self.tpm_types_h_file_content += "typedef  " + base_type + utils.indent(base_type) + name + ";\n"
        # end of loop - for row in table.rows:

        if table_dependence:  # if table dependence {*} found in table name
            self.tpm_types_h_file_content += "#endif   // TPM_ALG_" + table_dependence + "\n"
        # end of if else - if table dependence found

        self.marshaller.handle_simple_type_structures_new(table, tpm_alg_ids)
    # end of method - handle_typedeftable(self, f, table, tpm_alg_ids):

    # Handles data from Interface tables: writes type definition(s) based on table name into the header file content, by
    # interpreting the string inside the parentheses as the base type, and the string after it as the new type
    # If a new type name containing an algorithm type,type definitions are created with every corresponding algorithm ID
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table to be handled
    # tmp_alg_ids - mapping from algorithm types to list of corresponding algorithm IDs
    def handle_interface_table(self, table, tpm_alg_ids):
        base_type = utils.find_tpm_base_type_name(table.short_name)
        new_type = utils.find_tpm_type_name(table.short_name)

        typedef_statement = "typedef  " + base_type + utils.indent(base_type) + new_type + ";\n"
        alg_dep = utils.find_alg_constraints(table.name)
        if alg_dep:
            alg_name = "TPM_ALG_" + alg_dep
            typedef_statement_alg_dep = ""

            # check for !ALG
            alg_ids_list = utils.expand_alg_macro(new_type, tpm_alg_ids, alg_dep)
            # if new type name contains algorithm type, create type definition for all corresponding IDs
            for alg in alg_ids_list:
                alg_name = alg.name
                final_new_type = utils.replace_alg_placeholder(new_type, alg.short_name)
                typedef_statement_alg_dep += "#ifdef      " + alg_name + "\n"  # for each algorithm
                typedef_statement_alg_dep += "typedef  " + base_type + utils.indent(base_type) + final_new_type + ";\n"
                typedef_statement_alg_dep += "#endif   // " + alg_name + "\n"  # for each algorithm

            # in case there is no !ALG, create type definition for type found in table name
            if not typedef_statement_alg_dep:
                typedef_statement_alg_dep = "#ifdef      " + alg_name + "\n"
                typedef_statement_alg_dep += "typedef  " + base_type + utils.indent(base_type) + new_type + ";\n"
                typedef_statement_alg_dep += "#endif   // " + alg_name + "\n"

            typedef_statement = typedef_statement_alg_dep

        self.tpm_types_h_file_content += typedef_statement

        self.marshaller.handle_interface_table(table, tpm_alg_ids)
    # end of method - handle_interfacetable(self, f, table, tpm_alg_ids):

    # Handles data from Enum tables: writes type definition based on the table name and definitions (#define) of
    # constants, by interpreting the strings from the first column as the names, and the values from the second column
    # as the values
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table to be handled
    def handle_enum_table(self, table):
        base_type = utils.find_tpm_base_type_name(table.short_name)
        new_type = utils.find_tpm_type_name(table.short_name)

        self.tpm_types_h_file_content += "typedef  " + base_type + utils.indent(base_type) + new_type + ";\n"

        for row in table.rows:
            name = row[0]
            value = row[1].replace(" ", "")

            if name is u'' or "reserved" in name or "#" in name:  # skip those lines
                continue

            # write the define statement
            self.tpm_types_h_file_content += "#define  " + name + utils.indent(name) + "(" + new_type + ")(" + value + ")\n"

            # additionally write the TPM_RCS_* define
            if "RC_FMT1+" in value:
                name = name.replace("TPM_RC_", "TPM_RCS_")
                self.tpm_types_h_file_content += "#define  " + name + utils.indent(name) + "(" + new_type + ")(" + value + ")\n"
        # end of loop - for row in table.rows:

        self.marshaller.handle_advanced_type_structures(table)
    # end of method - handle_enumtable(self, f, table):

    # Handles data from Bits tables: writes type definition of structure, with members as bits or bit intervals, by
    # interpreting the values of the first column as the indexes of (a group of) bits, and the strings of the second
    # column as the name of these bits. Finally, this structure is created inside a union with an integral type of
    # the same size, for easier referencing in code.
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table to be handled
    def handle_bits_table(self, table):
        typedef_struct_name = utils.find_tpm_type_name(table.short_name)

        self.tpm_types_h_file_content += "typedef union {\n"
        self.tpm_types_h_file_content += "    struct {\n"

        size = 0
        for row in table.rows:
            bit = row[0]
            bitname = row[1]

            if "#" in bitname:
                continue

            nr_of_bits = 1
            if ":" in bit:
                values = bit.split(":")
                from_value = int(values[1])
                to_value = int(values[0])
                nr_of_bits = to_value - from_value + 1

            if "Reserved" in bitname:
                bitname = "Reserved_from_" + str(size)

            self.tpm_types_h_file_content += "        unsigned    " + bitname + utils.indent(bitname) + ": " + str(nr_of_bits) + ";\n"
            size += nr_of_bits
        # end of loop - for row in table.rows:

        self.tpm_types_h_file_content += "    };\n"
        self.tpm_types_h_file_content += "    UINT" + str(size) + " val;\n"
        self.tpm_types_h_file_content += "} " + typedef_struct_name + ";\n"

        self.marshaller.handle_bits_table(table)
    # end of method - handle_bitstable(self, f, table):

    # Creates a struct type definition, by interpreting the strings from the first column as member names, and the
    # strings from the second column as member types
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table, to get struct fields from
    # typedef_name - name of created struct type
    def handle_typedef_struct(self, table, typedef_name):
        self.tpm_types_h_file_content += "typedef struct {\n"

        for row in table.rows:
            parameter = row[0]
            member_type = row[1].replace("+", "")

            if "#" in parameter or "//" in parameter:
                continue

            # find constraints and remove them if found
            constraints = utils.find_alg_constraints(parameter)
            if constraints:
                parameter = parameter.replace("{" + constraints + "}", "").replace(" ", "")
                constraints = "[" + constraints.replace(":", "").strip() + "]"
            else:
                constraints = ""

            # find array size and include it in typedef struct if found
            size = utils.find_array_size(parameter)
            if size:
                size = size.replace(" ", "")
                parameter = parameter.replace(size, "")
                self.tpm_types_h_file_content += "    " + member_type + utils.indent(member_type, 5) + parameter.strip() + constraints + ";\n"
            else:
                self.tpm_types_h_file_content += "    " + member_type + utils.indent(member_type, 5) + parameter + ";\n"
        # end of loop - for row in table.rows:

        self.tpm_types_h_file_content += "} " + typedef_name + ";\n"

        self.marshaller.handle_structures_table(typedef_name, table)
    # end of method - handle_typedef_struct(self, f, table, typedef_name):

    # Creates a union type definition, with a struct inside it by interpreting the strings from the first column as
    # member names, and the strings from the second column as member types for the structure
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table, to get struct fields from
    # typedef_name - name of created union type
    def handle_typedef_union_struct(self, table, typedef_name):
        self.tpm_types_h_file_content += "typedef union {\n"
        self.tpm_types_h_file_content += "    struct {\n"

        for row in table.rows:
            parameter = row[0].replace("=", "")
            member_type = row[1].replace("+", "")

            if "#" in parameter:
                continue

            # find constraints and remove them if found
            constraints = utils.find_alg_constraints(parameter)
            if constraints:
                parameter = parameter.replace("{" + constraints + "}", "").replace(" ", "")
                constraints = constraints.replace(":", "")

            # find array size and include it in typedef struct if found
            size = utils.find_array_size(parameter)
            if size:
                parameter = parameter.replace(size, "")
                self.tpm_types_h_file_content += "        " + member_type + utils.indent(member_type, 1) + \
                                                 parameter + "[" + constraints.strip() + "]" + ";\n"
            else:
                self.tpm_types_h_file_content += "        " + member_type + utils.indent(member_type, 1) + \
                                                 parameter + ";\n"
        # end of loop - for row in table.rows:

        self.tpm_types_h_file_content += "    }            t;\n"
        self.tpm_types_h_file_content += "    " + "TPM2B" + "        b;\n"
        self.tpm_types_h_file_content += "} " + typedef_name + ";\n"

        self.marshaller.handle_structures_table(typedef_name, table)
    # end of method - def handle_typedef_union_struct(self, f, table, typedef_name):

    # Creates a union type definition, by interpreting the strings from the first column as
    # member names, and the strings from the second column as member types for the union. If the member name contains
    # an algorithm type, union members are created for each corresponding algorithm ID
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table, to get union fields from
    # typedef_name - name of created union type
    # tpm_alg_ids - mapping from algorithm types to list of corresponding algorithm IDs
    def handle_typedef_union(self, table, typedef_name, tpm_alg_ids):
        self.tpm_types_h_file_content += "typedef union {\n"

        for row in table.rows:
            parameter = row[0]
            member_type = row[1].replace("+", "")
            selector = row[2]

            if member_type == "" or "null" in parameter:
                continue

            member_string = ""

            # check for !ALG (algorithm type)
            algs = utils.expand_alg_macro(parameter, tpm_alg_ids)
            for alg in algs:
                dependence = alg.dependence
                if len(dependence) == 0:
                    dependence = alg.short_name

                alg_placeholder = selector.replace("TPM_ALG_", "")  # !ALG.*
                base_type = utils.replace_alg_placeholder(member_type, alg.short_name.upper())
                new_type = parameter.replace(alg_placeholder + "_DIGEST_SIZE", alg.short_name.upper() + "_DIGEST_SIZE").replace(" ", "")

                if alg_placeholder == "!ALG": # fix for Table 2:144
                    new_type = alg.short_name.lower()
                else:
                    new_type = new_type.replace(alg_placeholder, alg.short_name.lower())

                member_string += "#ifdef      TPM_ALG_" + dependence + "\n"
                member_string += "    " + base_type + utils.indent(member_type) + new_type + ";\n"
                member_string += "#endif   // TPM_ALG_" + dependence + "\n"
            # end of loop - for alg in algs:

            # in case there is no !ALG
            if not member_string:
                member_string = "    " + member_type + utils.indent(member_type) + parameter + ";\n"

                if selector:  # enclose with ifdef + endif
                    member_string = "#ifdef      " + selector + "\n" + member_string
                    member_string += "#endif   // " + selector + "\n"
            # end of if - if not member_string:

            self.tpm_types_h_file_content += member_string
        # end of loop - for row in table.rows:
        self.tpm_types_h_file_content += "} " + typedef_name + ";\n"

        self.marshaller.handle_union_table(table, tpm_alg_ids)
    # end of method - def handle_typedef_union(self, f, table, typedef_name, tpm_alg_ids):

    # Handles data from Structure or Union tables: delegates data handling to corresponding functions depending on
    # the type of the table, and surrounds contents written by these functions by define guards if applicable
    # Parameters:
    # table - internal representation of table to be handled
    # tpm_alg_ids - mapping from algorithm types to list of corresponding algorithm IDs
    def handle_structures_table(self, table, tpm_alg_ids):

        # handle TPMS_EMPTY structure
        if "TPMS_EMPTY" in table.short_name:
            self.tpm_types_h_file_content += "typedef BYTE TPMS_EMPTY;\n\n"
            self.marshaller.handle_structures_table_empty_structure(table)
            return

        # SELECTOR STARTBLOCK START
        selector = utils.find_alg_dep(table.short_name)
        if selector:
            self.tpm_types_h_file_content += "#ifdef      TPM_ALG_" + selector + "\n"
        # SELECTOR STARTBLOCK END

        typedef_name = utils.find_tpm_type_name(table.short_name)

        if "Structure" in table.short_name:
            if "TPM2B" in table.short_name: # TPM2B TYPEDEF UNION STRUCT
                self.handle_typedef_union_struct(table, typedef_name)
            else:  # TYPEDEF STRUCT
                self.handle_typedef_struct(table, typedef_name)

        if "Union" in table.short_name:  # TYPEDEF UNION
            self.handle_typedef_union(table, typedef_name, tpm_alg_ids)

        # SELECTOR ENDBLOCK START
        if selector:
            self.tpm_types_h_file_content += "#endif   // TPM_ALG_" + selector + "\n"
        # SELECTOR ENDBLOCK END
    # end of method - handle_structures_table(self, f, table, tpm_alg_ids):

    # Handles base types, by creating type definitions, interpreting the string from the first column of the table as
    # base type, and strings from the second column as the new type, and writing everything into a separate base types
    # header file BaseTypes.h
    # At the end, it calls the marshaller, to create marshalling functions for the table
    # Parameters:
    # table - internal representation of table with base types
    def create_base_types_h_file(self, table):
        base_types_h_file_content = BaseTypes.BASETYPE_HEADER
        base_types_h_file_content += "// Part 2, " + table.name + "\n"

        for row in table.rows:
            base_type = row[0]
            new_type = row[1]
            line = "typedef  " + base_type + utils.indent(base_type) + new_type + ";\n"
            base_types_h_file_content += str(line)

        base_types_h_file_content += "\n\n"

        self.marshaller.handle_simple_type_structures_new(table)

        base_types_h_file_content += BaseTypes.BASETYPE_FOOTER

        FileHandling.write_file(constants.TPM_INCLUDE_PATH + "BaseTypes.h", base_types_h_file_content)
    # end of method - write_base_types_file(self, table):

    # Handles all tables from Part 2 of the specification, delegating the handling of each table to functions, based on
    # the table types. For some special tables, it calls the marshalling directly, without any additional treatment.
    # Writes the results of the base type table handling into "BaseTypes.h", and the results of all
    # other tables into "TPM_Types.h"
    # Parameters:
    # table_list - list of all tables from Part 2 of the specification
    def create_tpm_types_h_file(self, table_list):
        tpm_alg_ids = None

        self.tpm_types_h_file_content = TpmTypes.TPMTYPES_HEADER

        print "Writing TPM_Types.h (and BaseTypes.h):"

        for table in table_list:
            print u"\t" + table.name.replace(u"—", "")  # "—" requires unicode

            if "Definition" not in table.name:
                continue
            if table.table_type is None:
                continue

            name = re.sub('\([^)]*\)\s*', "", table.short_name)
            name = re.sub('\{[^}]*\}\s*', "", name)
            self.tpm_types_h_file_content += "// Table 2:" + table.number + " - " + name + " (" + table.table_type + ")\n"

            # Base Types are a special case and will be written to BaseTypes.h (not TPM_Types.h)
            if "Base Types" in table.short_name:
                self.create_base_types_h_file(table)

            elif "TPM_ECC_CURVE Constants" in table.short_name:
                self.marshaller.handle_simple_constants(table)

            elif "TPM_CC Constants" in table.short_name:
                self.marshaller.handle_simple_constants(table)

                # TPM_ALG_IDs need further processing
            elif "TPM_ALG_ID Constants" in table.short_name:
                alg_id_inst = AlgorithmIDs()
                tpm_alg_ids = alg_id_inst.extract(table)
                self.marshaller.handle_simple_constants(table)

            elif "TypedefTable" in table.table_type:
                self.handle_typedef_table(table, tpm_alg_ids)

            elif "InterfaceTable" in table.table_type:
                self.handle_interface_table(table, tpm_alg_ids)

            elif "EnumTable" in table.table_type:
                self.handle_enum_table(table)

            elif "BitsTable" in table.table_type:
                self.handle_bits_table(table)

            elif "StructureTable" in table.table_type:
                self.handle_structures_table(table, tpm_alg_ids)

            elif "UnionTable" in table.table_type:
                self.handle_structures_table(table, tpm_alg_ids)
            self.tpm_types_h_file_content += "\n"
        # end of loop - for table in table_list:

        self.tpm_types_h_file_content += TpmTypes.TPMTYPES_FOOTER

        FileHandling.write_file(constants.TPM_INCLUDE_PATH + "TPM_Types.h", self.tpm_types_h_file_content)
    # end of method - write_files(self, table_list):

    # First function to be called from this class. It handles the license extraction, table extraction, table handling,
    # calls the marshalling for arrays itself, then writes the marshal file as well.
    # Parameters:
    # structures_file - file descriptor of Part 2 of the specification
    def extract(self, structures_file):
        # extract license text
        license_text = LicenseExtractor.extract_license(structures_file)
        FileHandling.set_license(license_text)

        # extract tables from document
        table_list = TableExtractor.extract_structure_tables(structures_file)

        # create TPM_Types.h (and BaseTypes.h)
        self.create_tpm_types_h_file(table_list)

        self.marshaller.handle_arrays()
        self.marshaller.write()

    # end of method - extract(self, structures_file):
