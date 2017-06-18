cmake_minimum_required(VERSION 3.0)

project(simulator)

include_directories(../src/include
                    ../src/platform/include
                    ../src/platform/include/prototypes
                    ../src/tpm/include
                    ../src/tpm/include/prototypes
                    ../src/simulator/include
                    ../src/simulator/include/prototypes
                    ../src/OsslCryptoEngine
                    ../lib)

FILE(GLOB sub-src ../src/*)
set_directory_properties(PROPERTIES ADDITIONAL_MAKE_CLEAN_FILES "${sub-src}")

#set(VERSION "01.16" CACHE STRING "01.16")
set(SPEC_VERSION "116" CACHE STRING "116")

if (UNIX)
	string(ASCII 27 Esc)
	set(ColorReset "${Esc}[m")
	set(Red         "${Esc}[31m")
	set(Green       "${Esc}[32m")
	set(Yellow      "${Esc}[33m")
	set(Blue        "${Esc}[34m")
	set(Magenta     "${Esc}[35m")
	set(Cyan        "${Esc}[36m")
	set(White       "${Esc}[37m")

        MESSAGE("${Green}Extracting source code for the TPM simulator version ${SPEC_VERSION} (this may take a while)${ColorReset}")
        execute_process(WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}/../scripts
                 COMMAND python main.py ${SPEC_VERSION}
                 RESULT_VARIABLE ret_var)
        
        if (${ret_var})
             if (${ret_var} EQUAL 1)
        	    MESSAGE(FATAL_ERROR "${Red}ERROR: Please update settings.py in the directory 'script'${ColorReset}")
             endif()
             if (${ret_var} GREATER 1)
                 MESSAGE(FATAL_ERROR "${Red}FATAL ERROR: ${ret_var}${ColorReset}")
             endif()
        endif()
        MESSAGE("${Green}Extraction finished${ColorReset}\n")
        
        # PATCH FILES
        add_subdirectory(patches)

endif()

# BUILD LIBRARIES
add_subdirectory(platform)

#if (${SPEC_VERSION} LESS "138")
    MESSAGE("${Green}Creating OsslCryptoEngine for the TPM simulator version ${SPEC_VERSION}${ColorReset}")
    add_subdirectory(OsslCryptoEngine)
#endif()

add_subdirectory(tpm)

# BUILD SIMULATOR
file(GLOB SIMULATOR_SOURCE_FILES "../src/simulator/*.c")
file(GLOB_RECURSE SIMULATOR_HEADER_FILES "../src/tpm/include/*.h")
include_directories(../src/include ../src/tpm/include/prototypes)
add_executable(Simulator ${SIMULATOR_SOURCE_FILES} ${SIMULATOR_HEADER_FILES})

add_dependencies(Simulator platform TPM)
#if (${SPEC_VERSION} LESS "138")
    MESSAGE("${Green}Adding OsslCryptoEngine dependency for the TPM simulator version ${SPEC_VERSION}${ColorReset}")
    add_dependencies(Simulator CryptoEngine)
#endif()




if(WIN32)
	set(PLATFORM_LIB "${CMAKE_CURRENT_BINARY_DIR}/platform/Debug/platform.lib")

    if (${SPEC_VERSION} LESS "138")
	set(CRYPTOENGINE_LIB "${CMAKE_CURRENT_BINARY_DIR}/OsslCryptoEngine/Debug/CryptoEngine.lib")
    endif()

	set(TPM_LIB "${CMAKE_CURRENT_BINARY_DIR}/tpm/Debug/TPM.lib")
endif()
if (UNIX)
	set(PLATFORM_LIB "${CMAKE_CURRENT_BINARY_DIR}/platform/libplatform.so")

#    if (${SPEC_VERSION} LESS "138")
	set(CRYPTOENGINE_LIB "${CMAKE_CURRENT_BINARY_DIR}/OsslCryptoEngine/libCryptoEngine.so")
#    endif()

	set(TPM_LIB "${CMAKE_CURRENT_BINARY_DIR}/tpm/libTPM.so")
endif()
target_link_libraries(Simulator ${PLATFORM_LIB} ${CRYPTOENGINE_LIB} ${TPM_LIB})


if (WIN32)
	target_link_libraries(Simulator wsock32 ws2_32 Rpcrt4)
endif()
if (UNIX)
	target_link_libraries(Simulator pthread dl)
endif()

# INSTALLATION
install (TARGETS Simulator DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/bin)
if(WIN32)
install (FILES "${CMAKE_CURRENT_BINARY_DIR}/platform/Debug/platform.dll"
         DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/bin)
install (FILES "${CMAKE_CURRENT_BINARY_DIR}/OsslCryptoEngine/Debug/CryptoEngine.dll"
         DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/bin)
install (FILES "${CMAKE_CURRENT_BINARY_DIR}/tpm/Debug/TPM.dll"
         DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/bin)
endif()
