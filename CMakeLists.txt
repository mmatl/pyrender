cmake_minimum_required(VERSION 3.14 FATAL_ERROR)
project(pyrender VERSION 1.0.0)

# Options
option(BUILD_PYTHON_WRAPPER "Build Python wrappers" OFF)

# Basic build settings
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

include(GNUInstallDirs)

# Add dependencies via CPM
include(cmake/CPM.cmake)

# Threads
find_package(Threads)

# SDL2
CPMAddPackage(
    NAME SDL2
    GIT_TAG release-2.30.12
    GIT_REPOSITORY https://github.com/libsdl-org/SDL.git
    OPTIONS
    "SDL_SHARED OFF"
    "SDL_STATIC ON"
)

# Filament (TNT)
CPMAddPackage("gh:google/filament#v1.56.8")

# Fmt
CPMAddPackage("gh:fmtlib/fmt#11.0.2")

# Collect sources and headers
set(SOURCE_FILES src/viewer.cpp)
set(HEADER_FILES include/pyrender/viewer.h)

# Collect library dependencies
set(LIBS
    filament
    SDL2::SDL2-static
    fmt
    Threads::Threads
)

# Create library library
add_library(${PROJECT_NAME} ${SOURCE_FILES} ${HEADER_FILES})
set_target_properties(${PROJECT_NAME} PROPERTIES VERSION ${PROJECT_VERSION} SOVERSION 1)
target_link_libraries(${PROJECT_NAME} PRIVATE ${LIBS})
target_include_directories(${PROJECT_NAME} PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)
target_include_directories(${PROJECT_NAME} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/src)
install(TARGETS ${PROJECT_NAME}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# Build Python Wrappers
if (BUILD_PYTHON_WRAPPER)
    add_subdirectory(pyrender)
endif()
