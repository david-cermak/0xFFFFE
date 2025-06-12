cmake_minimum_required(VERSION 3.10)

project(hello_world C)

# Set C standard
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Enable debug info and address sanitizer
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -g -fsanitize=address")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fsanitize=address")

# Create executable
add_executable(hello hello.c)
