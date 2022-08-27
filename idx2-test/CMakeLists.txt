cmake_minimum_required(VERSION 3.17)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(idx2-test CXX)

find_package(Threads REQUIRED)
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

target_link_libraries(idx2-test Threads::Threads)

