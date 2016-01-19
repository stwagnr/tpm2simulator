file(GLOB SOURCE_FILES "../../src/platform/*.c")

add_library(platform SHARED ${SOURCE_FILES})