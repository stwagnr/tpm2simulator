file(GLOB_RECURSE TPM_SOURCE_FILES "../../src/tpm/*.c")
file(GLOB_RECURSE TPM_HEADER_FILES "../../src/tpm/*.h")
file(GLOB_RECURSE TPM_HEADER_FILES2 "../../src/include/*.h")

list(REMOVE_ITEM TPM_SOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../src/tpm/include/CommandDispatchData.c)
list(REMOVE_ITEM TPM_SOURCE_FILES ${CMAKE_CURRENT_SOURCE_DIR}/../../src/tpm/include/CommandAttributeData.c)
include_directories(../../src/tpm/include ../../src/tpm/include/prototypes)

add_library(TPM SHARED 	${TPM_SOURCE_FILES}
						${TPM_HEADER_FILES} ${TPM_HEADER_FILES2})

target_compile_options(TPM PRIVATE -DSPEC_VERSION=${SPEC_VERSION})
add_dependencies(TPM platform CryptoEngine)

if(WIN32)
	set(PLATFORM_LIB "${CMAKE_CURRENT_BINARY_DIR}/../platform/Debug/platform.lib")
	set(CRYPTOENGINE_LIB "${CMAKE_CURRENT_BINARY_DIR}/../OsslCryptoEngine/Debug/CryptoEngine.lib")
endif()
if(UNIX)
	set(PLATFORM_LIB "${CMAKE_CURRENT_BINARY_DIR}/../platform/libplatform.so")
	set(CRYPTOENGINE_LIB "${CMAKE_CURRENT_BINARY_DIR}/../OsslCryptoEngine/libCryptoEngine.so")
    set(TEST_LINKER_LIB "-ldl")
endif()
target_link_libraries(TPM ${PLATFORM_LIB} ${CRYPTOENGINE_LIB} ${TEST_LINKER_LIB})

