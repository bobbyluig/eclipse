include(LsdSlamUtil)
lsd_slam_print_status("Setup required dependencies for LsdSlam tracking library")

##==============================================================================
## Boost
set(Boost_USE_STATIC_LIBS OFF) 
set(Boost_USE_MULTITHREADED ON)  
set(Boost_USE_STATIC_RUNTIME OFF)
if(WIN32)
  find_package(Boost REQUIRED COMPONENTS system thread)
else()
  find_package(Boost REQUIRED COMPONENTS system thread atomic)
endif()
if(Boost_FOUND)
  include_directories(${Boost_INCLUDE_DIRS})
  # cull_library_paths(Boost_LIBRARIES)
  set(LsdSlam_EXTERNAL_LIBS ${LsdSlam_EXTERNAL_LIBS} ${Boost_LIBRARIES})
  link_directories(${Boost_LIBRARY_DIR})
  lsd_slam_print_status("Boost libs: ${Boost_LIBRARIES}")
  set(Boost_BINARY_DIR ${Boost_LIBRARY_DIR})
endif(Boost_FOUND)

##==============================================================================
##  OpenCV
find_package(OpenCV REQUIRED)
get_filename_component(OpenCV_BINARY_DIR "${OpenCV_LIB_DIR}/../bin" ABSOLUTE)
include_directories(${OpenCV_INCLUDE_DIRS})
# cull_library_paths(OpenCV_LIBRARIES)
list(APPEND LsdSlam_EXTERNAL_LIBS ${OpenCV_LIBRARIES})
link_directories(${OpenCV_LIB_DIR})
lsd_slam_print_status("OpenCV include dirs:${OpenCV_INCLUDE_DIRS}")
lsd_slam_print_status("OpenCV libs:${OpenCV_LIBRARIES}")

##==============================================================================
# G2O
find_package(G2O REQUIRED)
set(G2O_BINARY_DIR ${G2O_ROOT}/bin)

set(G2O_LIBRARIES optimized ${G2O_CORE_LIBRARY} debug ${G2O_CORE_LIBRARY_DEBUG} 
                  optimized ${G2O_STUFF_LIBRARY} debug ${G2O_STUFF_LIBRARY_DEBUG}
                  optimized ${G2O_SOLVER_DENSE} debug ${G2O_SOLVER_DENSE_DEBUG}
                  optimized ${G2O_TYPES_SLAM3D} debug ${G2O_TYPES_SLAM3D_DEBUG}
                  optimized ${G2O_SIMULATOR} debug ${G2O_SIMULATOR_DEBUG}
                  )
if(G2O_SOLVER_CSPARSE AND NOT APPLE)
  if(WIN32)
    list(APPEND G2O_INCLUDE_DIR "${G2O_ROOT}/include/EXTERNAL/csparse")
    list(APPEND G2O_INCLUDE_DIR "$ENV{G2O_ROOT}/include/EXTERNAL/csparse")
  else()
    list(APPEND G2O_INCLUDE_DIR "/usr/include/suitesparse")
  endif()
  list(APPEND G2O_LIBRARIES ${G2O_SOLVER_CSPARSE}
                            ${G2O_SOLVER_CSPARSE_EXTENSION}
                            ${G2O_EXT_CSPARSE})
  add_definitions(-DHAVE_SOLVER_CSPARSE)
endif()
if(G2O_SOLVER_CHOLMOD)
  list(APPEND G2O_LIBRARIES ${G2O_SOLVER_CHOLMOD})
  add_definitions(-DHAVE_SOLVER_CHOLMOD)
endif()
if(G2O_SOLVER_EIGEN)
  list(APPEND G2O_LIBRARIES ${G2O_SOLVER_EIGEN})
  add_definitions(-DHAVE_SOLVER_EIGEN)
endif()

if(APPLE)
  find_package(CSparse REQUIRED)
  list(APPEND G2O_LIBRARIES ${CSPARSE_LIBRARY})
  list(APPEND EXTRA_INC_DIRS ${CSPARSE_INCLUDE_DIR})
else()
  link_directories(${G2O_ROOT}/lib)
endif()
include_directories(${G2O_INCLUDE_DIR})
# cull_library_paths(G2O_LIBRARIES)
list(APPEND LsdSlam_EXTERNAL_LIBS ${G2O_LIBRARIES})

##==============================================================================
# OpenGL
find_package(OpenGL)
lsd_slam_print_status("Found OpenGL ? ${OPENGL_FOUND}")
if(OPENGL_FOUND)
  lsd_slam_print_status("OpenGL INCLUDE: ${OPENGL_INCLUDE_DIR}")
  include_directories(${OPENGL_INCLUDE_DIR})
  list(APPEND LsdSlam_EXTERNAL_LIBS ${OPENGL_LIBRARIES})
endif()

# GLUT
find_package(GLUT)
if(GLUT_FOUND)
  include_directories(${GLUT_INCLUDE_DIR})
  list(APPEND LsdSlam_EXTERNAL_LIBS ${GLUT_LIBRARIES})
endif()

# GLEW
find_package(GLEW)
if(GLEW_FOUND)
  include_directories(${GLEW_INCLUDE_DIR})
  list(APPEND LsdSlam_EXTERNAL_LIBS ${GLEW_LIBRARIES})
endif()