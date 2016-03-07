cmake_minimum_required(VERSION 2.8)

set(PROJECT_NAME ORB_SLAM2)
project(${PROJECT_NAME})

IF(NOT CMAKE_BUILD_TYPE)
  SET(CMAKE_BUILD_TYPE Release)
ENDIF()

MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O3 -march=native")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native")

LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)

IF(WIN32)
	add_definitions("-DNOMINMAX")
	add_definitions("-DWINDOWS")
	add_definitions("-DORBSLAM_EXPORT")
	add_definitions("-DBOOST_ALL_NO_LIB")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
ENDIF()

set(OpenCV_STATIC OFF)
set(Boost_USE_STATIC_LIBS OFF)
find_package(OpenCV 3.0.0 REQUIRED)
find_package(Eigen3 3.1.0 REQUIRED)
find_package(Pangolin REQUIRED)
find_package(Boost COMPONENTS thread system chrono REQUIRED)

include_directories(
${PROJECT_SOURCE_DIR}
${PROJECT_SOURCE_DIR}/include
${EIGEN3_INCLUDE_DIR}
${Boost_INCLUDE_DIR}
${Pangolin_INCLUDE_DIRS}
${OpenCV_INCLUDE_DIRS}
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/dbow2
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/g2o
#${PYTHON_INCLUDE_DIR}
)

set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)

file(GLOB headers "include/*.h") #_RECURSE
file(GLOB sources "src/*.cc") #_RECURSE

add_library(${PROJECT_NAME} SHARED
${headers} ${sources}
)

link_directories(${Boost_LIBRARY_DIRS})

target_link_libraries(${PROJECT_NAME}
${OpenCV_LIBS}
${EIGEN3_LIBS}
${Boost_LIBRARIES}
#${PYTHON_LIBRARY}
${Pangolin_LIBRARIES}
${PROJECT_SOURCE_DIR}/Thirdparty/DBoW2/bin/Release/dbow2.lib
${PROJECT_SOURCE_DIR}/Thirdparty/g2o/bin/Release/g2o.lib
)

# Build examples

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D)

add_executable(rgbd_tum
Examples/RGB-D/rgbd_tum.cc)
target_link_libraries(rgbd_tum ${PROJECT_NAME})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Stereo)

add_executable(stereo_kitti
Examples/Stereo/stereo_kitti.cc)
target_link_libraries(stereo_kitti ${PROJECT_NAME})

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/Monocular)

add_executable(mono_tum
Examples/Monocular/mono_tum.cc)
target_link_libraries(mono_tum ${PROJECT_NAME})

add_executable(mono_kitti
Examples/Monocular/mono_kitti.cc)
target_link_libraries(mono_kitti ${PROJECT_NAME})

