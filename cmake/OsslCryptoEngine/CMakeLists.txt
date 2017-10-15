file(GLOB SOURCE_FILES "../../src/OsslCryptoEngine/*.c")

file(GLOB HEADER_FILES "../../lib/openssl/*.h")
file(GLOB HEADER_FILES2 "../../src/include/*.h")

include_directories(../../lib)

add_library(CryptoEngine SHARED ${SOURCE_FILES} ${HEADER_FILES} ${HEADER_FILES2})
add_dependencies(CryptoEngine platform)

if(CROSS OR ${CMAKE_SYSTEM_PROCESSOR} MATCHES "arm")
    target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/arm/libcrypto.a")
    target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/arm/libssl.a")
else(CROSS OR ${CMAKE_SYSTEM_PROCESSOR} MATCHES "arm")
    if(WIN32)
	    target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/libeay32.lib")
    endif()
    if(UNIX)
        if(CMAKE_SIZEOF_VOID_P EQUAL 8)
	        target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/x86-64/libcrypto.a")
	        target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/x86-64/libssl.a")
        else(CMAKE_SIZEOF_VOID_P EQUAL 8)
            target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/x86/libcrypto.a")
            target_link_libraries(CryptoEngine "${CMAKE_SOURCE_DIR}/../lib/x86/libssl.a")
        endif(CMAKE_SIZEOF_VOID_P EQUAL 8)
    endif()
endif(CROSS OR ${CMAKE_SYSTEM_PROCESSOR} MATCHES "arm")

if(WIN32)
	target_link_libraries(CryptoEngine
		"${CMAKE_CURRENT_BINARY_DIR}/../platform/Debug/platform.lib")
endif()
if(UNIX)
	target_link_libraries(CryptoEngine
		"${CMAKE_CURRENT_BINARY_DIR}/../platform/libplatform.so")
endif()
