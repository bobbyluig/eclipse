cmake_minimum_required(VERSION 2.8.7)

include("PythonMake.txt")


# Set default version to release.
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "Release")
endif()


# Tell MSVC to link Boost libraries statically.
if (MSVC)
    foreach(flag_var
		CMAKE_CXX_FLAGS CMAKE_CXX_FLAGS_DEBUG CMAKE_CXX_FLAGS_RELEASE
        CMAKE_CXX_FLAGS_MINSIZEREL CMAKE_CXX_FLAGS_RELWITHDEBINFO)
		if(${flag_var} MATCHES "/MD")
			string(REGEX REPLACE "/MD" "/MT" ${flag_var} "${${flag_var}}")
		endif()
	endforeach(flag_var)
   
    add_definitions(-DBOOST_PYTHON_STATIC_LIB)
    SET(Boost_USE_STATIC_LIBS ON)
    SET(Boost_USE_MULTITHREADED ON)
    SET(Boost_USE_STATIC_RUNTIME ON)
endif()


# Locate Boost and add include files.
set(Boost_NO_BOOST_CMAKE ON)

find_package(Boost 1.41.0 COMPONENTS python-py34)
if (NOT Boost_FOUND)
    find_package(Boost 1.41.0 COMPONENTS python)
endif()

if (NOT WIN32)
    set(BOOST_LIBRARYDIR ${BOOST_LIBRARYDIR} $ENV{BOOST_LIBRARYDIR}  
            /usr/lib/x86_64-linux-gnu/)
endif()

include_directories(${Boost_INCLUDE_DIRS})
message(STATUS "USING BOOST_LIBS: ${Boost_LIBRARIES}")


# Locate Python3, Numpy, and all libraries / includes.
find_python(3.5 3.4 PYTHON3_LIBRARY PYTHON3_INCLUDE_DIR
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


# Use ARM Neon and optimization on ARM-v7.
if(${CMAKE_SYSTEM_PROCESSOR} MATCHES "arm") 
	set(ARM_CXX_FLAGS "-O3 -mcpu=cortex-a5 -mfloat-abi=hard -mfpu=neon-fp16 -ffast-math")		
	set(CMAKE_CXX_FLAGS ${ARM_CXX_FLAGS})
	message(STATUS "Detected ARM processor. Will try to compile using NEON intrinsics rather than SSE2.")
endif()



# Ensure Position Independent Code on GCC.
if (CMAKE_COMPILER_IS_GNUCXX)
    add_definitions("-fPIC")
else()
    set(CMAKE_POSITION_INDEPENDENT_CODE True)
endif()


# Ensure GCC enables c++ 11 support.
if(CMAKE_COMPILER_IS_GNUCC)
    ADD_DEFINITIONS (-std=c++11)
endif(CMAKE_COMPILER_IS_GNUCC)


# Locate and add OpenCV.
set(OPENCV_DIR_HINT "")

if(WIN32)
    get_filename_component(OPENCV_DIR_PLATFORM $ENV{OPENCV_DIR} DIRECTORY)
    get_filename_component(OPENCV_DIR_HINT ${OPENCV_DIR_PLATFORM} DIRECTORY)
endif(WIN32)

set(OpenCV_STATIC OFF)
find_package(OpenCV REQUIRED HINTS ${OPENCV_DIR_HINT})


# Add all sources.
set(CF_CV_EXT_DIR "src/3rdparty/cv_ext")
set(CF_PIOTR_DIR "src/3rdparty/piotr")
set(CF_PBCVT_DIR "src/3rdparty/pbcvt")
set(CV_INPAINT_DIR "src/3rdparty/inpaint")
set(CF_EXPORTS_DIR "src/exports")

include_directories(${OpenCV_DIR}/include)
include_directories(${CF_TCLAP_DIR}
                    ${CF_CV_EXT_DIR}
                    ${CF_PIOTR_DIR}
                    ${CF_EXPORTS_DIR}
					${CV_INPAINT_DIR}/include
                    ${CF_PIOTR_DIR}/src
					${CF_PBCVT_DIR}/include)

include_directories(src/cf_libs/kcf
                    src/cf_libs/dsst
                    src/cf_libs/line2d
                    src/cf_libs/common)
					
file(GLOB PYTHON_EXPORTS
    "${CF_EXPORTS_DIR}/*.h"
    "${CF_EXPORTS_DIR}/*.cpp"
)
               
set(CF_PIOTR_SOURCES
    ${CF_PIOTR_DIR}/gradientMex.hpp
    ${CF_PIOTR_DIR}/src/gradientMex.cpp
    ${CF_PIOTR_DIR}/src/sse.hpp
    ${CF_PIOTR_DIR}/src/wrappers.hpp)

set(CF_LIB_COMMON_SOURCES
    src/cf_libs/common/feature_channels.hpp
    src/cf_libs/common/mat_consts.hpp
    src/cf_libs/common/math_helper.hpp
    src/cf_libs/common/math_helper.cpp
    src/cf_libs/common/scale_estimator.hpp
    src/cf_libs/common/cv_ext.hpp
	${CF_PBCVT_DIR}/src/pyboost_cv3_converter.cpp
    ${CF_CV_EXT_DIR}/shift.cpp
    ${CF_CV_EXT_DIR}/shift.hpp
    ${CF_CV_EXT_DIR}/math_spectrums.cpp
    ${CF_CV_EXT_DIR}/math_spectrums.hpp
    ${CF_CV_EXT_DIR}/psr.hpp
    ${CF_PIOTR_SOURCES}
	${CV_INPAINT_DIR}/src/template_match_candidates.cpp)
	
	
# Add Python module and link.
set(MODULE_NAME "oculus")
PYTHON_ADD_MODULE(${MODULE_NAME} src/oculus.cpp ${CF_LIB_COMMON_SOURCES} ${PYTHON_EXPORTS})
target_link_libraries(${MODULE_NAME} ${Boost_LIBRARIES} ${PYTHON3_LIBRARIES} ${OpenCV_LIBS})


# Configure installation.
message(STATUS "Module will be installed to: ${PYTHON3_PACKAGES_PATH}")
install(TARGETS ${MODULE_NAME} DESTINATION ${PYTHON3_PACKAGES_PATH})
