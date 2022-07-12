cmake_minimum_required(VERSION 3.8)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

project(idx2-test CXX)

find_package(idx2)

set(SOURCE_FILES idx2-test.cpp)

add_executable(idx2-test ${SOURCE_FILES})
#target_compile_features(idx2-test PUBLIC cxx_std_17)
target_link_libraries(idx2-test PUBLIC idx2)
