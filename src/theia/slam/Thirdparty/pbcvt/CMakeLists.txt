cmake_minimum_required(VERSION 2.8 FATAL_ERROR)
project("pbcvt")

#----------------------------CMAKE & GLOBAL PROPERTIES-------------------------#
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")

###============= C++11 support====================================
include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)

if(NOT MSVC)
	if(COMPILER_SUPPORTS_CXX11)
		set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
	elseif(COMPILER_SUPPORTS_CXX0X)
		set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
	else()
		message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
	endif()
endif()

#=============== Find Packages 
find_package(OpenCV COMPONENTS core)
find_package(Boost COMPONENTS python)
find_package(PythonInterp 3.4 REQUIRED)
find_package(PythonLibs 3.4 REQUIRED)
include("DetectPython")

# Locate Python3, Numpy, and all libraries / includes.
find_python(PYTHON3_LIBRARY PYTHON3_INCLUDE_DIR
    PYTHON3INTERP_FOUND PYTHON3_EXECUTABLE PYTHON3_VERSION_STRING
    PYTHON3_VERSION_MAJOR PYTHON3_VERSION_MINOR PYTHON3LIBS_FOUND
    PYTHON3LIBS_VERSION_STRING PYTHON3_LIBRARIES PYTHON3_LIBRARY
    PYTHON3_DEBUG_LIBRARIES PYTHON3_LIBRARY_DEBUG PYTHON3_INCLUDE_PATH
    PYTHON3_INCLUDE_DIR PYTHON3_INCLUDE_DIR2 PYTHON3_PACKAGES_PATH
    PYTHON3_NUMPY_INCLUDE_DIRS PYTHON3_NUMPY_VERSION)

#========pick python stuff========================================
SET(PYTHON_INCLUDE_DIRS ${PYTHON3_INCLUDE_DIR} ${PYTHON3_INCLUDE_DIR2} ${PYTHON3_NUMPY_INCLUDE_DIRS})
SET(PYTHON_LIBRARIES ${PYTHON3_LIBRARY})
SET(PYTHON_EXECUTABLE ${PYTHON3_EXECUTABLE})
SET(PYTHON_PACKAGES_PATH ${PYTHON3_PACKAGES_PATH})


file(GLOB project_sources ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)
message(STATUS "${project_sources}")

add_library(${PROJECT_NAME} SHARED ${project_sources} ${CMAKE_CURRENT_SOURCE_DIR}/include/pyboostcvconverter/pyboostcvconverter.hpp)
target_include_directories(${PROJECT_NAME} PUBLIC 
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
	${Boost_INCLUDE_DIRS} 
	${OpenCV_INCLUDE_DIRS} 
	${PYTHON_INCLUDE_DIRS} 
)

target_link_libraries(${PROJECT_NAME} 
	${Boost_LIBRARIES} 
	${OpenCV_LIBRARIES} 
	${PYTHON_LIBRARIES}
)

#---------------------------   INSTALLATION    -----------------------------------------------------
#-get proper extension for python binary shared object on this platform
execute_process(COMMAND ${PYTHON_EXECUTABLE} -c "import distutils.sysconfig; print distutils.sysconfig.get_config_var('SO')"
                RESULT_VARIABLE PYTHON_${PROJECT_NAME}_PY_PROCESS
                OUTPUT_VARIABLE ${PROJECT_NAME}_PY_SUFFIX
                OUTPUT_STRIP_TRAILING_WHITESPACE)

set_target_properties(${PROJECT_NAME} PROPERTIES
                      PREFIX ""
                      OUTPUT_NAME "pbcvt"
                      SUFFIX "${${PROJECT_NAME}_PY_SUFFIX}")

if(MSVC AND NOT PYTHON_DEBUG_LIBRARIES)
  set(PYTHON_INSTALL_CONFIGURATIONS CONFIGURATIONS Release)
else()
  set(PYTHON_INSTALL_CONFIGURATIONS "")
endif()

if(WIN32)
  set(PYTHON_INSTALL_ARCHIVE "")
else()
  set(PYTHON_INSTALL_ARCHIVE ARCHIVE DESTINATION ${PYTHON_PACKAGES_PATH} COMPONENT python)
endif()

install(TARGETS ${PROJECT_NAME}
      ${PYTHON_INSTALL_CONFIGURATIONS}
      RUNTIME DESTINATION ${PYTHON_PACKAGES_PATH} COMPONENT python
      LIBRARY DESTINATION ${PYTHON_PACKAGES_PATH} COMPONENT python
      ${PYTHON_INSTALL_ARCHIVE}
 )

