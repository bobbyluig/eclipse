cmake_minimum_required(VERSION 2.8)

set(PROJECT_NAME ORB_SLAM2)
project(${PROJECT_NAME})

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

message("Build type: " ${CMAKE_BUILD_TYPE})

list(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)
include("FindPython")

if(WIN32)
	add_definitions(-DNOMINMAX)
	add_definitions(-DWINDOWS)
	add_definitions(-DORBSLAM_EXPORT)
	add_definitions(-DBOOST_ALL_NO_LIB)
	add_definitions(-DBOOST_PYTHON_STATIC_LIB)
	
	set(Boost_USE_STATIC_LIBS ON)
	set(Boost_USE_MULTITHREADED ON)
    set(Boost_USE_STATIC_RUNTIME ON)
	
	if(MSVC)
		foreach(flag_var
			CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
			CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
			if(${flag_var} MATCHES "/MD")
				string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
			endif()
		endforeach(flag_var)
	endif()
else()
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -march=native")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")
endif()

set(OpenCV_STATIC OFF)
find_package(OpenCV 3.0.0 REQUIRED)
find_package(Eigen3 3.1.0 REQUIRED)
find_package(PythonInterp 3.4 REQUIRED)
find_package(PythonLibs 3.4 REQUIRED)
find_package(Boost COMPONENTS python REQUIRED)

# Locate Python3, Numpy, and all libraries / includes.
find_python(PYTHON3_LIBRARY PYTHON3_INCLUDE_DIR
    PYTHON3INTERP_FOUND PYTHON3_EXECUTABLE PYTHON3_VERSION_STRING
    PYTHON3_VERSION_MAJOR PYTHON3_VERSION_MINOR PYTHON3LIBS_FOUND
    PYTHON3LIBS_VERSION_STRING PYTHON3_LIBRARIES PYTHON3_LIBRARY
    PYTHON3_DEBUG_LIBRARIES PYTHON3_LIBRARY_DEBUG PYTHON3_INCLUDE_PATH
    PYTHON3_INCLUDE_DIR PYTHON3_INCLUDE_DIR2 PYTHON3_PACKAGES_PATH
    PYTHON3_NUMPY_INCLUDE_DIRS PYTHON3_NUMPY_VERSION)
	
if(NOT PYTHON3_EXECUTABLE OR NOT PYTHON3_INCLUDE_DIR OR NOT PYTHON3_LIBRARY OR NOT PYTHON3_PACKAGES_PATH)
	message(SEND_ERROR "Some or all parts of Python3 - PYTHON3_EXECUTABLE, PYTHON3_INCLUDE_DIR, PYTHON3_LIBRARY, or PYTHON3_PACKAGES_PATH were not found.")
endif()

if(NOT PYTHON3_NUMPY_INCLUDE_DIRS)
	message(SEND_ERROR "Numpy was not found. Please set PYTHON3_NUMPY_INCLUDE_DIRS manually.")
endif()

include_directories(${PYTHON3_NUMPY_INCLUDE_DIRS})

if (PYTHON3_INCLUDE_PATH)
	include_directories(${PYTHON3_INCLUDE_PATH})
else()
	include_directories(${PYTHON3_INCLUDE_DIR})
endif()

message(STATUS "USING PYTHON_LIBS: ${PYTHON3_LIBRARY}")

# Ensure Position Independent Code on GCC.
if (CMAKE_COMPILER_IS_GNUCXX)
    add_definitions("-fPIC")
else()
    set(CMAKE_POSITION_INDEPENDENT_CODE True)
endif()

include_directories(
${PROJECT_SOURCE_DIR}
${PROJECT_SOURCE_DIR}/include
${EIGEN3_INCLUDE_DIR}
${Boost_INCLUDE_DIR}
${OpenCV_INCLUDE_DIRS}
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/dbow2
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/g2o
${PROJECT_SOURCE_DIR}/Thirdparty/pbcvt/include
${PROJECT_SOURCE_DIR}/python/include
)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

file(GLOB headers "include/*.h") #_RECURSE
file(GLOB sources "src/*.cc") #_RECURSE

add_library(${PROJECT_NAME} STATIC
${headers} ${sources}
)

link_directories(${Boost_LIBRARY_DIRS})

target_link_libraries(${PROJECT_NAME}
${OpenCV_LIBS}
${EIGEN3_LIBS}
${Boost_LIBRARIES}
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/bin/Release/dbow2.lib
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/bin/Release/g2o.lib
)

# Copy DLLs
list(APPEND ExternalSharedLibs
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/bin/Release/dbow2.dll
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/bin/Release/g2o.dll
)

file(INSTALL ${ExternalSharedLibs} DESTINATION ${PYTHON3_PACKAGES_PATH})

# Add Python module and link.
set(MODULE_NAME "pyslam")
PYTHON_ADD_MODULE(${MODULE_NAME}
${PROJECT_SOURCE_DIR}/python/src/pyslam.cpp 
${PROJECT_SOURCE_DIR}/python/src/pyboost_cv3_converter.cpp
)

target_link_libraries(${MODULE_NAME}
${PROJECT_NAME}
${PYTHON3_LIBRARIES}
${Boost_LIBRARIES}
)

# Configure installation.
message(STATUS "Module will be installed to: ${PYTHON3_PACKAGES_PATH}")
install(TARGETS ${MODULE_NAME} DESTINATION ${PYTHON3_PACKAGES_PATH})