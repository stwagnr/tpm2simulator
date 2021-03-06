file(GLOB_RECURSE TPM_SOURCE_FILES "../../src/tpm/*.c")
file(GLOB_RECURSE TPM_SOURCE_FILES2 "../../src/OsslCryptoEngine/*.c")
file(GLOB_RECURSE TPM_HEADER_FILES "../../src/tpm/*.h")
file(GLOB_RECURSE TPM_HEADER_FILES2 "../../src/include/*.h")

SET(GCC_COMPILE_FLAGS "-DSPEC_VERSION=${SPEC_VERSION}")
add_definitions(${GCC_COMPILE_FLAGS})
SET( CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} ${GCC_COMPILE_FLAGS}" )

list(REMOVE_ITEM TPM_SOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../src/tpm/include/CommandDispatchData.c)
list(REMOVE_ITEM TPM_SOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../src/tpm/include/CommandAttributeData.c)
if (${SPEC_VERSION} EQUAL "138")
    list(REMOVE_ITEM TPM_SOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../src/tpm/crypt/CryptDataEcc.c)
endif()
include_directories(../../src/tpm/include ../../src/tpm/include/prototypes)

if (${SPEC_VERSION} LESS "138")
	add_library(TPM SHARED 	${TPM_SOURCE_FILES}
							${TPM_HEADER_FILES} ${TPM_HEADER_FILES2})
endif()
if ((${SPEC_VERSION} GREATER "138") OR (${SPEC_VERSION} EQUAL "138"))
	add_library(TPM SHARED 	${TPM_SOURCE_FILES} ${TPM_SOURCE_FILES2}
							${TPM_HEADER_FILES} ${TPM_HEADER_FILES2})
endif()

target_compile_options(TPM PRIVATE -DSPEC_VERSION=${SPEC_VERSION})
if (${SPEC_VERSION} LESS "138")
    add_dependencies(TPM CryptoEngine)
endif()
add_dependencies(TPM platform)

if(WIN32)
	set(PLATFORM_LIB "${CMAKE_CURRENT_BINARY_DIR}/../platform/Debug/platform.lib")
	set(CRYPTOENGINE_LIB "${CMAKE_CURRENT_BINARY_DIR}/../OsslCryptoEngine/Debug/CryptoEngine.lib")
endif()
if(UNIX)
	set(PLATFORM_LIB "${CMAKE_CURRENT_BINARY_DIR}/../platform/libplatform.so")
	set(CRYPTOENGINE_LIB "${CMAKE_CURRENT_BINARY_DIR}/../OsslCryptoEngine/libCryptoEngine.so")
    set(TEST_LINKER_LIB "-ldl")
endif()
if (${SPEC_VERSION} LESS "138")
target_link_libraries(TPM ${CRYPTOENGINE_LIB})
endif()
target_link_libraries(TPM ${PLATFORM_LIB} ${TEST_LINKER_LIB})
if ((${SPEC_VERSION} GREATER "138") OR (${SPEC_VERSION} EQUAL "138"))
    if(UNIX)
        if(CMAKE_SIZEOF_VOID_P EQUAL 8)
            MESSAGE("Link x86-64 openssl to simulator: ${CMAKE_SOURCE_DIR}/../lib/x86-64")
            target_link_libraries(TPM "${CMAKE_SOURCE_DIR}/../lib/x86-64/libcrypto.a")
            target_link_libraries(TPM "${CMAKE_SOURCE_DIR}/../lib/x86-64/libssl.a")
        else(CMAKE_SIZEOF_VOID_P EQUAL 8)
            MESSAGE("Link x86 openssl to simulator: ${CMAKE_SOURCE_DIR}/../lib/x86")
            target_link_libraries(TPM "${CMAKE_SOURCE_DIR}/../lib/x86/libcrypto.a")
            target_link_libraries(TPM "${CMAKE_SOURCE_DIR}/../lib/x86/libssl.a")
        endif(CMAKE_SIZEOF_VOID_P EQUAL 8)
    endif()
endif()

