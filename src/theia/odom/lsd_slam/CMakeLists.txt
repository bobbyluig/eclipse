cmake_minimum_required(VERSION 2.8.9)
project(lsd_slam)

include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# Sources & headers ============================================================
set(modules depth_estimation global_mapping io_wrapper model tracking util)
set(lsd_slam_srcs)
foreach(module ${modules})
  file(GLOB ${module}_srcs ${CMAKE_CURRENT_SOURCE_DIR}/${module}/*.cc
                           ${CMAKE_CURRENT_SOURCE_DIR}/${module}/*.cpp
                           ${CMAKE_CURRENT_SOURCE_DIR}/${module}/*.h)
  include_directories(${CMAKE_CURRENT_SOURCE_DIR}/${module})
  list(APPEND lsd_slam_srcs ${${module}_srcs})
endforeach(module ${modules})

file(GLOB other_srcs ${CMAKE_CURRENT_SOURCE_DIR}/*.cc
                     ${CMAKE_CURRENT_SOURCE_DIR}/*.h)
list(APPEND lsd_slam_srcs ${other_srcs})

## the library
set(lib_target lsd_slam)
add_library(${lib_target} ${lsd_slam_srcs})
set_property(TARGET ${lib_target} PROPERTY FOLDER "lsd_slam/libs")

target_link_libraries(${lib_target} ${LsdSlam_ALL_LIBRARIES})
list(APPEND LsdSlam_ALL_LIBRARIES ${lib_target})
lsd_slam_print_status("LsdSlam_ALL_LIBRARIES slam:${LsdSlam_ALL_LIBRARIES}")