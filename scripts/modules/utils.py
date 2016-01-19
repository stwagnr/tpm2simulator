# -*- coding: utf-8 -*-

import re
import os
import codecs

from modules import constants
from modules.part2_structures.marshal import tpm2_partx_type_mapping


# Generates string containing a calculated number of spaces, used for indentation
# Parameters:
# string
# extra
# Returns:
# indented string
def indent(string, extra=0):
    return (constants.INDENT - len(string) + extra) * " "


# Converts indentation of given text
# Parameters:
# text_p
# Return xml tag containing indented string
def convert_indentation(text_p):
    text_ss = text_p.findAll(constants.XML_TEXT_S)
    for text_s in text_ss:
        if text_s.has_attr(constants.XML_TEXT_C):
            text_s.replaceWith(int(text_s[constants.XML_TEXT_C]) * " ")
    return text_p


# Extracts algorithm dependency (string from inside curly brackets)
# Parameters:
# string_with_curly_brackets
# Returns:
# algorithm dependency of found
def find_alg_dep(string_with_curly_brackets):
    result = re.search('\{(.*)\}', string_with_curly_brackets)
    if result:
        return result.group(1)
    else:
        return None


# Extracts base type from table title (string from inside brackets)
# Parameters:
# tpm_table_title
# Returns:
# base type if found
def find_tpm_base_type_name(tpm_table_title):
    result = re.search('\((.*)\)', tpm_table_title)
    if result:
        return result.group(1)
    else:
        return None


# Extracts new type from table title (last type in title)
# Parameters:
# tpm_table_title
# Returns
# new type, if found
def find_tpm_type_name(tpm_table_title):
    result = re.search('\s([^{RSA|ECC}|(][A-Z][A-Z][!A-Z._2]*)', tpm_table_title)
    if result:
        return result.group(1)
    else:
        return None


# Extracts algorithm constraints from string with curly brackets
# Parameters:
# string_with_curly_brackets
# Returns:
# algorithms constraint
def find_alg_constraints(string_with_curly_brackets):
    return find_alg_dep(string_with_curly_brackets)


# Extracts array size from string with curly brackets
# Parameters:
# string_with_curly_brackets
# Returns:
# array size
def find_array_size(string_with_square_brackets):
    result = re.search('(\[(.*)\])', string_with_square_brackets)
    if not result:
        return None
    return result.group(1)


# Finds algorithm type name in macro, and returns the list of corresponding algorithm IDs
# Returns:
# the algorithm IDs corresponding to the types found in macro
def expand_alg_macro(macro, tpm_alg_ids, alg_dep=None):
    result = re.search('!ALG([a-zA-Z.]*)', macro)
    if not result:
        return []

    types = result.group(1).split('.')
    types = [t for t in types if t]
    alg_ids = []
    for alg_type in types:
        # print("types: {0} - alg_type={1} (algdep: {2})".format(types, alg_type, alg_dep))

        sel = "!ALG." + alg_type
        alg_ids = alg_ids + tpm_alg_ids[sel.upper()]
        # print("upper: {0} vs lower: {1}".format(sel.upper(), sel))
        if alg_type.islower():
            for key in tpm_alg_ids.keys():
                if sel.upper() in key and key != sel.upper():
                    alg_ids = alg_ids + tpm_alg_ids[key]

    if alg_dep and ("ECC" in alg_dep or "RSA" in alg_dep):
        tmp_list = []
        for alg in alg_ids:
            if str(alg_dep) in alg.dependence:
                tmp_list.append(alg)
        alg_ids = tmp_list

    return alg_ids
# end of method - expand_alg_macro(macro, tpm_alg_ids, alg_dep=None):


# Extracts short algorithm name, from long format
# Parameters:
# alg
# Returns
# short algorithm name, if found
def extract_alg_name(alg):
    result = re.search('TPM_ALG_([0-9a-zA-Z_]*)', alg)
    if result is not None:
        return result.group(1)


# Replaces algorithm type name with algorithm ID
# Parameters:
# pattern_with_ALG
# name
# Returns:
# string with algorithm ID substituted
def replace_alg_placeholder(pattern_with_ALG, name):
    name = name.replace("TPM_ALG_", "")
    result = re.sub('!ALG.?[^_\s]*', name, pattern_with_ALG)
    if result is not None:
        return result
    else:
        return ""


# Extracts base type size, if available
# Parameters:
# base_type
# Returns:
# size of base type, or nothing
def find_base_type_size(base_type):
    result = re.search("(int|INT)([1368][246]*)", base_type)
    if result:
        return result.group(2)
    else:
        return None


# Extracts basic base type from base type
# Parameters:
# base_type
# Returns:
# basic base type
def find_basic_base_type(base_type):
    while base_type in tpm2_partx_type_mapping.dictionary.keys() \
            and tpm2_partx_type_mapping.dictionary[base_type][0] is not None\
            and "int" not in tpm2_partx_type_mapping.dictionary[base_type][0]:
        base_type = tpm2_partx_type_mapping.dictionary[base_type][0]
    return base_type


# Finds config (string from inside the angle brackets
# Parameters:
# string_with_angle_bracket
# Returns:
# config
def find_config(string_with_angle_bracket):
    config = re.search('<(.*)>', string_with_angle_bracket)
    if config:
        config = config.group(1)
    elif "TPM_CAP Constants" in string_with_angle_bracket:
        config = "IN/OUT"
    else:
        config = ""
    return config


# Splits row according to the list of offsets
# Parameters:
# line - string containing row to split
# offsets - list of indexes in the string
# Returns:
# res - list of strings resulting from the splitting
def split_row(line, offsets):
    start = 0
    res = []
    offset_list = list(offsets)
    for o in offset_list[1:]:
        if "  " not in line and "#" not in line:
            return None
        res.append(line[start:o].strip())
        start = o
    res.append(line[start:])
    return res


# Checks certain conditions about given row
# Parameters:
# row
# Returns:
# boolean value containing result of the conditions
def is_handle(row):
    positives = any(r in row[0] for r in ["_DH_", "_SH_", "_HANDLE"]) or \
                any(r in row[1] for r in ["Handle", "nvIndex", "@"])
    negatives = all(r not in row[1] for r in ["persistentHandle", "flushHandle", "pcrNum"])
    return positives and negatives
