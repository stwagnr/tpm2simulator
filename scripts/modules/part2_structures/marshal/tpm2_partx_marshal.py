# -*- coding: utf-8 -*-

import re
import settings
from modules import constants
from modules import utils
from modules.part2_structures.marshal.tpm2_partx_marshal_simple_type import SimpleMarshaller
from modules.part2_structures.marshal.tpm2_partx_marshal_advanced_type import AdvancedMarshaller
from modules.part2_structures.marshal.tpm2_partx_marshal_bits_table import BitsTableMarshaller
from modules.part2_structures.marshal.tpm2_partx_marshal_interface_table import InterfaceTableMarshaller
from modules.part2_structures.marshal.tpm2_partx_marshal_structure_table import StructureTableMarshaller
from modules.part2_structures.marshal.tpm2_partx_marshal_union_table import UnionTableMarshaller
from modules.part2_structures.marshal.tpm2_partx_marshal_array import ArrayMarshaller
from modules.part2_structures.marshal import tpm2_partx_type_mapping
from modules.part2_structures.marshal import tpm2_partx_marshal_templates
from modules.file_handling import FileHandling


# Class that contains marshal handling functions for all table types, as well as an instances of SimpleMarshaller and
# subclasses of SimpleMarshaller, used by the handling functions in order to generate marshalling source code
class Marshaller:

    # Initialises paths to destination files of marshalling source code, and instantiates all marshalling subclasses
    def __init__(self):
        if settings.SPEC_VERSION_INT < 138:
            self.file_path = constants.SRC_PATH + constants.TPM_PATH + "/support/marshal.c"
            self.file_path_fp = constants.SRC_PATH + constants.TPM_PATH + "/include/prototypes/marshal_fp.h"
        else:
            self.file_path = constants.SRC_PATH + constants.TPM_PATH + "/support/Marshal.c"
            self.file_path_fp = constants.SRC_PATH + constants.TPM_PATH + "/include/prototypes/Marshal_fp.h"
        self.file = None

        self.content = u""
        self.content_fp = u""

        # Create marshallers
        self.simple_marshaller = SimpleMarshaller()
        self.advanced_marshaller = AdvancedMarshaller()
        self.bits_table_marshaller = BitsTableMarshaller()
        self.interface_table_marshaller = InterfaceTableMarshaller()
        self.structure_table_marshaller = StructureTableMarshaller()
        self.union_table_marshaller = UnionTableMarshaller()
        self.array_marshaller = ArrayMarshaller()

        # Initialize dictionaries
        self.array_functions = dict()
        self.function_prototypes_with_flag = dict()

    # Creates header comment for a specific table and adds it to the contents of marshal files
    # Parameters:
    # table - internal representation of the table, containing the metainformation about itself to generate comment
    def create_header_comment(self, table):
        self.content += "\n// Table 2:" + table.number + " - " + table.short_name + " (" + table.table_type + ")\n"
        self.content_fp += "\n// Table 2:" + table.number + " - " + table.short_name + " (" + table.table_type + ")\n"

    # Checks if base type already present in type mapping dictionary
    # Parameters:
    # base_type - string containing name of base type
    # Returns:
    # base type - string containing name of base type
    # boolean value - representing the availability of the base type in the dictionary
    @staticmethod
    def handle_base_types(base_type):
        if "int" in base_type:
            for entry in tpm2_partx_type_mapping.dictionary.iteritems():
                if entry[1][0] == base_type or entry[1][0] == "u"+base_type:
                    base_type = entry[0]
                    return base_type, True
        return base_type, False

    # Handle marshalling for Typedef tables and BaseType tables by calling required functions from SimpleMarshaller
    # For every base type that contains an algorithm type, marshaling functions are generated for each algorithm,
    # (if not already done or already defined) surrounded by define guards (ifdefs)
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    # tpm_alg_ids -  mapping from algorithm types to list of corresponding algorithm IDs
    def handle_simple_type_structures_new(self, table, tpm_alg_ids=None):

        self.create_header_comment(table)

        for row in table.rows:
            base_type = row[0]
            new_type = row[1]

            types_list = []

            # check for !ALG
            alg_dep = utils.find_alg_constraints(table.short_name)
            algs = utils.expand_alg_macro(new_type, tpm_alg_ids, alg_dep)
            for alg in algs:
                typedef = utils.replace_alg_placeholder(new_type, alg.short_name)
                types_list.append(typedef)
            # end of loop - for alg in alg_list:

            # in case there is no !ALG
            if not algs:
                types_list = [new_type]

            # handle the (list of) typ(es) in the current row
            for current_type in types_list:

                if alg_dep:
                    self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)
                    self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)

                # check if type is a C base type and already in mapping dictionary
                base_type, c_base_type = self.handle_base_types(base_type)

                already_marshaled = base_type in tpm2_partx_type_mapping.dictionary.keys()
                unsigned_marshaled = "u"+base_type in tpm2_partx_type_mapping.dictionary.keys()

                if unsigned_marshaled:
                    base_type = "u"+base_type

                if c_base_type or already_marshaled or unsigned_marshaled:
                    # if original type was already marshaled somehow
                    # marshalling new type would be redundant - change to define for new type
                    orig_mrshl = tpm2_partx_type_mapping.dictionary[base_type]
                    orig_table_nr = orig_mrshl[1]

                    # recursive exploration of most basic base_type in mapping dictionary
                    base_type = utils.find_basic_base_type(base_type)

                    # add a comment that points to the origin of the type definition
                    self.content += "//   " + base_type + " definition used from Table 2:" + orig_table_nr + "\n"

                    self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_defined.format(current_type)
                    self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(current_type)

                    self.content_fp += self.simple_marshaller.create_unmarshal_fp_define(current_type, base_type)
                    self.content_fp += self.simple_marshaller.create_marshal_fp_define(current_type, base_type)

                else:
                    # handle base types: figure out the size
                    size = utils.find_base_type_size(base_type)
                    if not size:  # skip base type without size (i.e. 'int', which is used for 'BOOL')
                        continue

                    self.content += self.simple_marshaller.create_unmarshal_code(current_type, int(size)/8)
                    self.content += self.simple_marshaller.create_marshal_code(current_type, int(size)/8)

                    self.content_fp += self.simple_marshaller.create_unmarshal_fp(current_type)
                    self.content_fp += self.simple_marshaller.create_marshal_fp(current_type)

                if unsigned_marshaled:
                    base_type = base_type[1:]

                tpm2_partx_type_mapping.dictionary[current_type] = [base_type, table.number]
                # done with the new type

                if alg_dep:
                    self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
                    self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)

                self.content += "\n"
                self.content_fp += "\n"
        # end of loop - for row in table.rows:
    # end of method - handle_simple_type_structures_new(self, table, tpm_alg_ids):

    # Handle marshalling for special tables, which are not used to create constant or type definitions, by calling
    # required functions from SimpleMarshaller, if base type found in table name not already marshaled
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    def handle_simple_constants(self, table):

        self.create_header_comment(table)

        base_type = utils.find_tpm_base_type_name(table.short_name)
        current_type = utils.find_tpm_type_name(table.short_name)

        alg_dep = utils.find_alg_dep(table.short_name)

        size = utils.find_base_type_size(base_type)
        if not size:
            return

        if alg_dep:
            self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)
            self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)

        already_marshaled = base_type in tpm2_partx_type_mapping.dictionary.keys()

        if already_marshaled:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_defined.format(current_type)
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(current_type)

            self.content_fp += self.simple_marshaller.create_unmarshal_fp_define(current_type, base_type)
            self.content_fp += self.simple_marshaller.create_marshal_fp_define(current_type, base_type)
        else:
            self.content += self.simple_marshaller.create_unmarshal_code(current_type, int(size)/8)
            self.content += self.simple_marshaller.create_marshal_code(current_type, int(size)/8)

            self.content_fp += self.simple_marshaller.create_unmarshal_fp(current_type)
            self.content_fp += self.simple_marshaller.create_marshal_fp(current_type)

        tpm2_partx_type_mapping.dictionary[current_type] = [base_type, table.number]

        if alg_dep:
            self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
            self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
    # end of method - handle_simple_constants(self, table):

    # Handle marshalling for Enum tables by calling
    # required functions from AdvancedMarshaller, based on in/out declarations in table name
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    def handle_advanced_type_structures(self, table):

        self.create_header_comment(table)

        base_type = utils.find_tpm_base_type_name(table.short_name)
        current_type = utils.find_tpm_type_name(table.short_name)

        config = utils.find_config(table.name)

        size = utils.find_base_type_size(base_type)
        if not size:
            return

        in_declaration = re.search('([iI])', config)
        out_declaration = re.search('([oO])', config)
        s_declaration = re.search('([S])', config)

        cases = []
        rc_fail = None
        for row in table.rows:
            name = row[0]
            if "#" in name:
                rc_fail = name.replace("#", "")
            elif "TPM_CAP_FIRST" in name or "TPM_CAP_LAST" in name:
                continue  # skip
            else:
                cases.append(name)

        # in
        if in_declaration is None:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_not_req.format(current_type)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_not_req.format(current_type)

        else:
            if (base_type in tpm2_partx_type_mapping.dictionary.keys() or s_declaration) and not rc_fail:
                self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_defined.format(current_type)
                self.content_fp += self.advanced_marshaller.create_unmarshal_fp_define(current_type, base_type)

            else:
                self.content += self.advanced_marshaller.create_unmarshal_code(current_type, base_type, cases,rc_fail)
                self.content_fp += self.advanced_marshaller.create_unmarshal_fp(current_type)

        # out
        if out_declaration is None:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_not_req.format(current_type)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_not_req.format(current_type)
        else:
            if base_type in tpm2_partx_type_mapping.dictionary.keys() or s_declaration:
                self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(current_type)
                self.content_fp += self.advanced_marshaller.create_marshal_fp_define(current_type, base_type)

            else:
                self.content += self.advanced_marshaller.create_marshal_code(current_type, size)
                self.content_fp += self.advanced_marshaller.create_marshal_fp(current_type)

        tpm2_partx_type_mapping.dictionary[current_type] = [base_type, table.number]
    # end of method - handle_advanced_type_structures(self, table):

    # Handle marshalling for Bits tables by calling required functions from BitsTableMarshaller based on the base type
    # found in table name, if base type not already marshaled
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    def handle_bits_table(self, table):

        self.create_header_comment(table)

        base_type = utils.find_tpm_base_type_name(table.short_name)
        current_type = utils.find_tpm_type_name(table.short_name)

        reserved = 0
        i = 0
        for row in table.rows:
            bit_idx = row[0]
            bit_name = row[1]

            bits = 1
            if ":" in bit_idx and "Reserved" in bit_name:
                values = bit_idx.split(":")
                from_value = int(values[1])
                to_value = int(values[0])

                for b in range(from_value, to_value+1):
                    reserved |= (1 << b)

            elif "Reserved" in bit_name:
                reserved |= (1 << i)
            i += bits
        # end of loop - for row in table.rows:

        # generate a bit mask starting with 0x...
        reserved = "0x%0.2X" % reserved

        result = re.search("(int|INT)([1368][246]*)", base_type)
        if result:
            size = result.group(2)
        elif base_type in tpm2_partx_type_mapping.dictionary.keys() and tpm2_partx_type_mapping.dictionary[base_type]:
            size = tpm2_partx_type_mapping.dictionary[base_type][0]
        else:
            return

        # in
        if base_type in tpm2_partx_type_mapping.dictionary.keys() and reserved == "0x00":
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_defined.format(current_type)
            self.content_fp += self.bits_table_marshaller.create_unmarshal_fp_define(current_type, base_type)

        else:
            self.content += self.bits_table_marshaller.create_unmarshal_code(current_type, base_type, reserved, None)
            self.content_fp += self.bits_table_marshaller.create_unmarshal_fp(current_type)

        # out
        if base_type in tpm2_partx_type_mapping.dictionary.keys():
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(current_type)
            self.content_fp += self.bits_table_marshaller.create_marshal_fp_define(current_type, base_type)

        else:
            self.content += self.bits_table_marshaller.create_marshal_code(current_type, size)
            self.content_fp += self.bits_table_marshaller.create_marshal_fp(current_type)

        tpm2_partx_type_mapping.dictionary[current_type] = [base_type, table.number]
    # end of method - handle_bits_table(self, table):

    # Handle marshalling for Interface tables by calling
    # required functions from InterfaceTableMarshaller based on in/out declarations in table name,
    # using definition guards (ifdefs) when necessary
    # It interprets the table as multiple tables, in the case that an algorithm type name is found in the table name
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    # tpm_alg_ids -  mapping from algorithm types to list of corresponding algorithm IDs
    def handle_interface_table(self, table, tpm_alg_ids):

        self.create_header_comment(table)

        bool_flag = False

        base_type = utils.find_tpm_base_type_name(table.short_name)
        current_type = utils.find_tpm_type_name(table.short_name)

        # config block begin
        config = re.search('<(.*)>', table.name)
        if config:
            config = config.group(1)
        else:
            config = "IN/OUT"

        in_declaration = re.search('([iI])', config)
        out_declaration = re.search('([oO])', config)
        # s_declaration = re.search('([S])', config)

        # config block end

        # distinguish between a normal case, when a simple table needs to be processed
        # and a case, where a table represents multiple tables (see table 124)
        alg_dep = None
        if "!" not in current_type:
            result = re.search('\{(.*)\}', table.name)
            if result:
                alg_dep = result.group(1)

        cases = []
        alg_list = []
        checks = []
        conditions = None
        rc_fail = None
        for row in table.rows:
            value_name = row[0]

            if "{" in value_name:
                values = value_name.split(":")
                from_value = values[0].replace("{", "")
                to_value = values[1].replace("}", "")
                checks.append([from_value.strip(), to_value.strip()])

            elif "+TPM" in value_name:
                conditions = value_name.replace("+", "")
                self.function_prototypes_with_flag[current_type] = ""
                bool_flag = True

            elif "$RSA_KEY_SIZES_BITS" in value_name:
                cases = constants.RSA_KEY_SIZES_BITS

            elif "$ECC_CURVES" in value_name:
                cases = constants.ECC_CURVES

            elif "#" not in value_name:
                if "$!ALG" in value_name:
                    alg_list += utils.expand_alg_macro(value_name, tpm_alg_ids, alg_dep)
                elif "!ALG" in value_name:
                    alg_list += utils.expand_alg_macro(value_name, tpm_alg_ids, alg_dep)
                else:
                    cases.append(value_name)
            else:
                rc_fail = value_name.replace("#", "")
        # end of loop - for row in table.rows:

        if "!ALG.S" in current_type:
            # interpret the table as multiple tables
            for alg in alg_list:
                # symmetric algorithm in question
                alg_name = re.search(r'TPM_ALG_(.*)', alg.name)
                alg_name = alg_name.group(1)
                # substitute '!ALG.S' part in the value with the ALG name
                val = re.sub(r'!ALG\.S', alg_name, current_type)

                self.content += "// Table 2:" + table.number + " - " \
                    + table.short_name.replace("{!ALG.S} (TPM_KEY_BITS) ", "").replace("!ALG.S", alg_name) \
                    + "  (" + table.table_type + ")\n"
                self.content_fp += "// Table 2:" + table.number + " - " \
                    + table.short_name.replace("{!ALG.S} (TPM_KEY_BITS) ", "").replace("!ALG.S", alg_name) \
                    + "  (" + table.table_type + ")\n"

                # manually set individual alg_deps
                self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_name)
                self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_name)

                # utilize cases for individual sizes of the supported ALG sizes
                cases = constants.S_KEY_SIZES[alg.name]
                self.content += self.interface_table_marshaller.create_unmarshal_code(
                    val, base_type, cases, None, checks, conditions, rc_fail)
                self.content_fp += self.interface_table_marshaller.create_unmarshal_fp(val)

                # out
                self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(val)
                self.content_fp += self.interface_table_marshaller.create_marshal_fp_define(val, base_type)

                # manually set individual alg_deps
                self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_name)
                self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_name)
            # end of loop - for alg in alg_list:

        else:
            if alg_dep:
                self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)
                self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)

            # in
            if in_declaration:
                self.content += self.interface_table_marshaller.create_unmarshal_code(
                    current_type, base_type, cases, alg_list, checks, conditions, rc_fail)
                self.content_fp += self.interface_table_marshaller.create_unmarshal_fp(current_type, bool_flag)

            # out
            if out_declaration:
                if base_type in tpm2_partx_type_mapping.dictionary.keys():
                    self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(current_type)
                    self.content_fp += self.interface_table_marshaller.create_marshal_fp_define(
                        current_type, base_type)
                else:
                    self.content += self.interface_table_marshaller.create_marshal_code(current_type, base_type)
                    self.content_fp += self.interface_table_marshaller.create_marshal_fp(current_type)

            if alg_dep:
                self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
                self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)

        tpm2_partx_type_mapping.dictionary[current_type] = [base_type, table.number]
    # end of method - handle_interface_table(self, table, tpm_alg_ids):

    # Handle marshalling for Structures tables by calling required functions from StructureTableMarshaller based on
    # in/out declarations in table name, using definition guards (ifdefs) when necessary
    # Parameters:
    # typedef_name - type of the generated marshaling functions
    # table - internal representation of the table, based on which marshaling functions are generated
    def handle_structures_table(self, typedef_name, table):
        self.create_header_comment(table)

        bool_flag = False

        result = re.search('<(.*)>', table.name)
        if result:
            config = result.group(1)
        else:
            config = "IN/OUT"

        in_declaration = re.search('([iI])', config)
        out_declaration = re.search('([oO])', config)

        alg_dep = utils.find_alg_constraints(table.name)

        for row in table.rows:
            parameter = row[0]
            member_type = row[1]

            if "+TPM" in member_type:
                self.function_prototypes_with_flag[typedef_name] = ""
                bool_flag = True
            if "[count]" in parameter or "[size]" in parameter:
                self.array_functions[member_type] = [alg_dep, config]
        # end of loop - for row in table.rows:

        if alg_dep:
            self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)
            self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)

        if in_declaration is None:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_not_req.format(typedef_name)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_not_req.format(typedef_name)

        if len(table.rows) == 1:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_defined.format(typedef_name)
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_defined.format(typedef_name)
            only_row = table.rows[0]
            parameter = only_row[0]
            member_type = only_row[1]

            if member_type.endswith("+"):

                self.content_fp += self.structure_table_marshaller.create_unmarshal_fp_define(
                    typedef_name,
                    member_type.replace("+", ""),
                    parameter,
                    1)
                self.content_fp += self.structure_table_marshaller.create_marshal_fp_define(
                    typedef_name,
                    member_type.replace("+", ""),
                    parameter,
                    1)
            else:
                self.content_fp += self.structure_table_marshaller.create_unmarshal_fp_define(
                    typedef_name,
                    member_type,
                    parameter,
                    0)
                self.content_fp += self.structure_table_marshaller.create_marshal_fp_define(
                    typedef_name,
                    member_type,
                    parameter,
                    0)

        else:
            # in
            if in_declaration:
                self.content += self.structure_table_marshaller.create_unmarshal_code(
                    typedef_name, table, self.function_prototypes_with_flag)
                self.content_fp += self.structure_table_marshaller.create_unmarshal_fp(typedef_name, bool_flag)

            # out
            if out_declaration:
                self.content += self.structure_table_marshaller.create_marshal_code(
                    typedef_name, table, self.function_prototypes_with_flag)
                self.content_fp += self.structure_table_marshaller.create_marshal_fp(typedef_name)

        if out_declaration is None:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_not_req.format(typedef_name)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_not_req.format(typedef_name)

        if alg_dep:
            self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
            self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)

        tpm2_partx_type_mapping.dictionary[typedef_name] = [None, table.number]
    # end of method - handle_structures_table(self, value, table):

    # Handle marshalling for empty structures using StructureTableMarshaller for function prototypes
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    def handle_structures_table_empty_structure(self, table):
        if settings.SPEC_VERSION_INT < 138:
            self.content += tpm2_partx_marshal_templates.TPMS_EMPTY_UNMARSHAL_pre138
            self.content += tpm2_partx_marshal_templates.TPMS_EMPTY_MARSHAL_pre138
        else:
            self.content += tpm2_partx_marshal_templates.TPMS_EMPTY_UNMARSHAL
            self.content += tpm2_partx_marshal_templates.TPMS_EMPTY_MARSHAL
        self.content_fp += self.structure_table_marshaller.create_unmarshal_fp("TPMS_EMPTY")
        self.content_fp += self.structure_table_marshaller.create_marshal_fp("TPMS_EMPTY")

        tpm2_partx_type_mapping.dictionary["TPMS_EMPTY"] = [None, table.number]
    # end of method - handle_structures_table_empty_structure(self):

    # Handle marshalling for Union tables by calling
    # required functions from UnionTableMarshaller based on in/out declarations in table name
    # Parameters:
    # table - internal representation of the table, based on which marshaling functions are generated
    # tpm_alg_ids -  mapping from algorithm types to list of corresponding algorithm IDs
    def handle_union_table(self, table, tpm_alg_ids):

        self.create_header_comment(table)

        current_type = utils.find_tpm_type_name(table.short_name)

        alg_dep = re.search('{(.*)}', table.short_name)
        if alg_dep:
            alg_dep = alg_dep.group(1)

        result = re.search('<(.*)>', table.name)
        if result:
            config = result.group(1)
        else:
            config = "IN/OUT"

        in_declaration = re.search('([iI])', config)
        out_declaration = re.search('([oO])', config)

        if alg_dep:
            self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)
            self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)

        # in
        if in_declaration:
            self.content += self.union_table_marshaller.create_unmarshal_code(
                current_type,
                table.rows,
                tpm_alg_ids,
                self.function_prototypes_with_flag)
            self.content_fp += self.union_table_marshaller.create_unmarshal_fp(current_type)
        else:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_not_req.format(current_type)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Unmarshal_not_req.format(current_type)

        # out
        if out_declaration:
            self.content += self.union_table_marshaller.create_marshal_code(
                current_type,
                table.rows,
                tpm_alg_ids,
                self.function_prototypes_with_flag)
            self.content_fp += self.union_table_marshaller.create_marshal_fp(current_type)
        else:
            self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_not_req.format(current_type)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Marshal_not_req.format(current_type)

        if alg_dep:
            self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
            self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
    # end of method - handle_union_table(self, table, tpm_alg_ids):

    # Handle marshalling for arrays by calling required functions from ArrayMarshaller based on in/out declarations
    # in the list of array functions, using definition guards (ifdefs) when necessary
    def handle_arrays(self):

        for function in self.array_functions:

            bool_flag = False

            # add comment for marshalling/unmarshalling of arrays (see Part 4, Section 4)
            self.content += tpm2_partx_marshal_templates.COMMENT_Array_Un_Marshal_TYPE.format(function)
            self.content_fp += tpm2_partx_marshal_templates.COMMENT_Array_Un_Marshal_TYPE.format(function)

            alg_dep = self.array_functions[function][0]
            config = self.array_functions[function][1]

            in_declaration = re.search('([iI])', config)
            out_declaration = re.search('([oO])', config)

            if alg_dep:
                self.content += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)
                self.content_fp += tpm2_partx_marshal_templates.IFDEF_ALG.format(alg_dep)

            if function in self.function_prototypes_with_flag.keys():
                bool_flag = True

            # in
            if in_declaration:
                self.content += self.array_marshaller.create_unmarshal_code(function, bool_flag)
                self.content_fp += self.array_marshaller.create_unmarshal_fp(function, bool_flag)
            else:
                self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Array_Unmarshal_not_req.format(function)
                self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Array_Unmarshal_not_req.format(function)
            # out
            if out_declaration:
                self.content += self.array_marshaller.create_marshal_code(function)
                self.content_fp += self.array_marshaller.create_marshal_fp(function)
            else:
                self.content += tpm2_partx_marshal_templates.COMMENT_TYPE_Array_Marshal_not_req.format(function)
                self.content_fp += tpm2_partx_marshal_templates.COMMENT_TYPE_Array_Marshal_not_req.format(function)

            if alg_dep:
                self.content += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
                self.content_fp += tpm2_partx_marshal_templates.ENDIF_ALG.format(alg_dep)
    # end of method -handle_arrays(self):

    # Create marshaling source files with FileHandler at path defined in the constructor, containing marshaling
    # functions based on the tables
    def write(self):
        if settings.SPEC_VERSION_INT < 138:
            self.content = u'#include    "InternalRoutines.h"\n\n' + self.content
        else:
            self.content = u'#include    "Tpm.h"\n\n' + self.content

        # marshal.c
        FileHandling.write_file(self.file_path, self.content)

        # marshal_fp.h
        self.content_fp = u'#ifndef    _MARSHAL_FP_H\n\
                            #define    _MARSHAL_FP_H\n\n'\
                          + self.content_fp
        self.content_fp += "#endif // _MARSHAL_FP_H"
        FileHandling.write_file(self.file_path_fp, self.content_fp)
    # end of method - write(self)
