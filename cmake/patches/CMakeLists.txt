MESSAGE("${Green}Patching files${ColorReset}\n")

file(GLOB PATCH_FILES "../../patches/${SPEC_VERSION}/*.patch")

FIND_PROGRAM(PATCH_BIN NAMES patch PATHS /usr/bin/ /bin)

if(PATCH_BIN STREQUAL PATCH_BIN-NOTFOUND)
	MESSAGE(FATAL_ERROR "${Red}Error: patch binaries not found. Please install the patch package.${ColorReset}\n")
else()
	MESSAGE(STATUS "${Green}Patch binaries found.${ColorReset}\n")
endif()

foreach(ITR ${PATCH_FILES})
	MESSAGE("Attempting to apply patch file '${ITR}'")
	execute_process(WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/../src
			COMMAND patch -p1 -r - --no-backup-if-mismatch -s -N --ignore-whitespace
			INPUT_FILE ${ITR}
			RESULT_VARIABLE ret_var
			OUTPUT_VARIABLE out)
	if (${out} MATCHES ".*FAILED")
		MESSAGE(STATUS "${Red}Error in patch '${ITR}':${ColorReset}")
		MESSAGE(STATUS "${Red}${out}${ColorReset}")
	endif()
	MESSAGE("${Green}Patch file successfully applied${ColorReset}\n")
endforeach()

MESSAGE("${Green}Patching finished${ColorReset}\n")
