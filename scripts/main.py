# -*- coding: utf-8 -*-

from collections import OrderedDict
import sys
import settings
import logging

# tpm2 class imports
from modules.file_handling import FileHandling
import modules.part2_structures.tpm2_part2_structures as structures
import modules.part3_commands.tpm2_part3_commands as commands

import modules.part4_spt_routines.tpm2_part4_spt_routines_header_files as spt_routines_header_files
import modules.part4_spt_routines.tpm2_part4_spt_routines as spt_routines
import modules.part4_spt_routines.tpm2_part4_spt_routines_annex as spt_routines_annex


# --------------------------------------------------------------------------- #
# Check settings
# --------------------------------------------------------------------------- #
if len(sys.argv) == 2 and len(sys.argv[1]) == 3 and sys.argv[1].startswith("1"):
    print "updating version to " + sys.argv[1]
    settings.update_spec(sys.argv[1])

if not settings.SET:
    print "Please check and set the values in 'settings.py'"
    exit(1)

# --------------------------------------------------------------------------- #
# Dictionary with mappings of sections to folders
# --------------------------------------------------------------------------- #

# Dictionary: commands
dict_sections_commands = OrderedDict([
    ("Start-up", "Startup"),
    ("Testing", "Testing"),
    ("Session Commands", "Session"),
    ("Object Commands", "Object"),
    ("Duplication Commands", "Duplication"),
    ("Asymmetric Primitives", "Asymmetric"),
    ("Symmetric Primitives", "Symmetric"),
    ("Random Number Generator", "Random"),
    ("Hash/HMAC/Event Sequences", "HashHMAC"),
    ("Attestation Commands", "Attestation"),
    ("Ephemeral EC Keys", "Ecdaa"),
    ("Signing and Signature Verification", "Signature"),
    ("Command Audit", "CommandAudit"),
    ("Integrity Collection (PCR)", "PCR"),
    ("Enhanced Authorization (EA) Commands", "EA"),
    ("Hierarchy Commands", "Hierarchy"),
    ("Dictionary Attack Functions", "DA"),
    ("Miscellaneous Management Functions", "Misc"),
    ("Field Upgrade", "FieldUpgrade"),
    ("Context Management", "Context"),
    ("Clocks and Timers", "ClockTimer"),
    ("Capability Commands", "Capability"),
    ("Non-volatile Storage", "NVStorage"),
    ("Vendor Specific", "Vendor"),  # Version 1.19+
])

# Dictionary: supporting routines header files
dict_sections_spt_routines_header_files = OrderedDict([
    ("Header Files", "include")
])

# Dictionary: supporting routines
dict_sections_spt_routines = OrderedDict([
    ("Main", "main"),
    ("Command Support Functions", None),
    ("Subsystem", "subsystem"),
    ("Support", "support"),
    ("Cryptographic Functions", "crypt"),
])

# Dictionary: supporting routines annex
if settings.SPEC_VERSION_INT < 138:
    dict_sections_spt_routines_annex = OrderedDict([
        ("(informative) Implementation Dependent", "include"),
        ("(informative) Cryptographic Library Interface", "../OsslCryptoEngine"),
        ("(informative) Simulation Environment", "../platform"),
        ("(informative) Remote Procedure Interface", "../simulator"),
    ])
else:
    dict_sections_spt_routines_annex = OrderedDict([
        ("(informative) Implementation Dependent", "include"),
        ("(informative) Library-Specific", "../OsslCryptoEngine"),
        ("(informative) Simulation Environment", "../platform"),
        ("(informative) Remote Procedure Interface", "../simulator"),
    ])

# --------------------------------------------------------------------------- #
# Extract code from PDF/XML files
# --------------------------------------------------------------------------- #

# Create class instances:
s = structures.Structures()
c = commands.Commands()
h = spt_routines_header_files.SptRoutinesHeaderFiles()
r = spt_routines.SptRoutines()
a = spt_routines_annex.SptRoutinesAnnex()

file_handler = FileHandling()

# Extract code:
print "Reading " + settings.TPM20_SPEC_STRUCTURES
structures_file = file_handler.get_fd(settings.TPM20_SPEC_STRUCTURES)
print ""
s.extract(structures_file)

print ""
print "Reading " + settings.TPM20_SPEC_COMMANDS
sys.stdout.flush()
commands_file = file_handler.get_fd(settings.TPM20_SPEC_COMMANDS)
print ""
c.extract(commands_file, dict_sections_commands)

print ""
print "Reading " + settings.TPM20_SPEC_SUPPORTING_ROUTINES
sys.stdout.flush()
support_file = file_handler.get_fd(settings.TPM20_SPEC_SUPPORTING_ROUTINES)
print ""
h.extract(support_file, dict_sections_spt_routines_header_files)
r.extract(support_file, dict_sections_spt_routines)
a.extract(support_file, dict_sections_spt_routines_annex)

print ""
if FileHandling.warn_pyastyle:
    logging.warning(" pyastyle not found! Please run 'pip install pyastyle' for formatted output.")
