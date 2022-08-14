cmake_minimum_required(VERSION 3.17)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(idx2-test CXX)
include_directories(${CMAKE_SOURCE_DIR}/nanobind/include)
add_subdirectory(nanobind)
find_package(Python REQUIRED COMPONENTS Development)
find_package(Threads REQUIRED)
#find_package(idx2)

set(SOURCE_FILES idx2-test.cpp idx2.hpp)

add_executable(idx2-test ${SOURCE_FILES})
target_compile_features(idx2-test PUBLIC cxx_std_17)
if (MSVC)
  target_compile_definitions(idx2-test PUBLIC -D_CRT_SECURE_NO_WARNINGS)
  target_compile_options(idx2-test PUBLIC /Zc:preprocessor /Zc:__cplusplus /wd5105)
  target_link_options(idx2-test PUBLIC dbghelp.lib)
elseif (UNIX)
  target_compile_options(idx2-test PUBLIC -Wno-format-zero-length)
endif()
#target_compile_definitions(idx2-test PUBLIC -Didx2_Avx2)
#target_link_libraries(idx2-test PUBLIC idx2)

target_link_libraries(idx2-test Threads::Threads Python)

nanobind_add_module(
  idx2Nasa
  NB_STATIC # Build static libnanobind (the extension module itself remains a shared library)
  idx2-test.cpp
)



set_target_properties(idx2Nasa PROPERTIES CMAKE_POSITION_INDEPENDENT_CODE ON)
target_compile_features(idx2Nasa PUBLIC cxx_std_17)
if (MSVC)
  target_compile_definitions(idx2Nasa PUBLIC -D_CRT_SECURE_NO_WARNINGS)
  target_compile_options(idx2Nasa PUBLIC /Zc:preprocessor /Zc:__cplusplus /wd5105)
  target_link_options(idx2Nasa PUBLIC dbghelp.lib)
elseif (UNIX)
  target_compile_options(idx2Nasa PUBLIC -Wno-format-zero-length)
endif()

install(TARGETS idx2Nasa LIBRARY DESTINATION .)
