# -*- coding: utf-8 -*-

SPEC_VERSION = "01.16"
SPEC_VERSION_INT = 116
SPEC_PATH = "../documents/116/"

PUBLISHED_SPEC_VERSIONS = ["01.16", "01.38"]

DATA_ORIGIN_PDF_TXT = (SPEC_VERSION in PUBLISHED_SPEC_VERSIONS)

FILE_ENDING = ".txt"
if not DATA_ORIGIN_PDF_TXT:
    FILE_ENDING = ".fodt"

TPM20_SPEC_STRUCTURES = SPEC_PATH + "TPM Rev 2.0 Part 2 - Structures " + SPEC_VERSION + FILE_ENDING
TPM20_SPEC_COMMANDS = SPEC_PATH + "TPM Rev 2.0 Part 3 - Commands " + SPEC_VERSION + "-code" + FILE_ENDING
TPM20_SPEC_SUPPORTING_ROUTINES = SPEC_PATH + "TPM Rev 2.0 Part 4 - Supporting Routines " + SPEC_VERSION + "-code" + FILE_ENDING

# not (yet) supported
ENABLE_TABLE_DRIVEN_DISPATCHER = False


def update_spec(version):
    global SPEC_VERSION, SPEC_VERSION_INT, SPEC_PATH
    global DATA_ORIGIN_PDF_TXT
    global ENABLE_TABLE_DRIVEN_DISPATCHER
    global TPM20_SPEC_STRUCTURES, TPM20_SPEC_COMMANDS, TPM20_SPEC_SUPPORTING_ROUTINES

    SPEC_VERSION = "0" + version[0] + "." + version[1:3]
    SPEC_VERSION_INT = int(version)
    SPEC_PATH = "../documents/" + version + "/"
    DATA_ORIGIN_PDF_TXT = (SPEC_VERSION in PUBLISHED_SPEC_VERSIONS)

    # not (yet) supported
    # if version > 116:
    #	ENABLE_TABLE_DRIVEN_DISPATCHER = True

    if DATA_ORIGIN_PDF_TXT:
        FILE_ENDING = ".txt"
    else:
        FILE_ENDING = ".fodt"

    TPM20_SPEC_STRUCTURES = SPEC_PATH + "TPM Rev 2.0 Part 2 - Structures " + SPEC_VERSION + FILE_ENDING
    TPM20_SPEC_COMMANDS = SPEC_PATH + "TPM Rev 2.0 Part 3 - Commands " + SPEC_VERSION + "-code" + FILE_ENDING
    TPM20_SPEC_SUPPORTING_ROUTINES = SPEC_PATH + "TPM Rev 2.0 Part 4 - Supporting Routines " + SPEC_VERSION + "-code" + FILE_ENDING
# end of function "update_spec(version)"


##########################################################
# tpm/include/Vendor_String.h
# ---------------------------
MANUFACTURER = "StWa"               # 4 characters
VENDOR_STRING_1 = "AISE"            # 4 characters
FIRMWARE_V1 = "(0x20160601)"        # "(0xYYYYMMDD)"
##########################################################


##########################################################
# Change to "True" after setting the correct values above
##########################################################
SET = False
##########################################################
