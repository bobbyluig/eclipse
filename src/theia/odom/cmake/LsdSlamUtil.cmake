## Nice colors in command ======================================================
if(NOT WIN32)
  string(ASCII 27 Esc)
  set(LsdSlam_COLOR_NORMAL          "")
  set(LsdSlam_COLOR_RESET           "${Esc}[m")
  set(LsdSlam_COLOR_BOLD            "${Esc}[1m")
  set(LsdSlam_COLOR_RED             "${Esc}[31m")
  set(LsdSlam_COLOR_GREEN           "${Esc}[32m")
  set(LsdSlam_COLOR_YELLOW          "${Esc}[33m")
  set(LsdSlam_COLOR_BLUE            "${Esc}[34m")
  set(LsdSlam_COLOR_MAGENTA         "${Esc}[35m")
  set(LsdSlam_COLOR_CYAN            "${Esc}[36m")
  set(LsdSlam_COLOR_BOLD_RED        "${Esc}[1;31m")
  set(LsdSlam_COLOR_BOLD_GREEN      "${Esc}[1;32m")
  set(LsdSlam_COLOR_BOLD_YELLOW     "${Esc}[1;33m")
  set(LsdSlam_COLOR_BOLD_BLUE       "${Esc}[1;34m")
  set(LsdSlam_COLOR_BOLD_MAGENTA    "${Esc}[1;35m")
  set(LsdSlam_COLOR_BOLD_CYAN       "${Esc}[1;36m")
  set(LsdSlam_COLOR_BG_RED          "${Esc}[41m")
  set(LsdSlam_COLOR_BG_GREEN        "${Esc}[42m")
  set(LsdSlam_COLOR_BG_YELLOW       "${Esc}[43m")
  set(LsdSlam_COLOR_BG_BLUE         "${Esc}[44m")
  set(LsdSlam_COLOR_BG_MAGENTA      "${Esc}[45m")
  set(LsdSlam_COLOR_BG_CYAN         "${Esc}[46m")
endif(NOT WIN32)

## Useful commands  ============================================================
# Cull out paths in given list of libs and keep names
macro(cull_library_paths LIBS)
  set(IN_LIBS ${${LIBS}})
  set(${LIBS} "")
  foreach(CULL_LIB ${IN_LIBS})
    get_filename_component(FN "${CULL_LIB}" NAME)
    list(APPEND ${LIBS} ${FN})
  endforeach()
endmacro(cull_library_paths)

# To add apps folder from external directories
macro(lsd_slam_add_external_apps_path in_directory in_binary_path in_message)
  if(EXISTS ${in_directory})
    message(STATUS ${in_message})
    add_subdirectory(${in_directory}  ${in_binary_path})
  else()
    message(WARNING "Input directory ${in_directory} not exists")
  endif()
endmacro(lsd_slam_add_external_apps_path)

# To print nice message with information about the source file
# Output: file_name:: message
macro(lsd_slam_print_status_colorized color msg)
  get_filename_component(CURRENT_FILENAME "${CMAKE_CURRENT_LIST_FILE}" NAME)
  get_filename_component(CURRENT_PATH "${CMAKE_CURRENT_LIST_FILE}" PATH)
  get_filename_component(CURRENT_PARENT_DIRECTORY "${CURRENT_PATH}" NAME)
  message(STATUS "${color}${CURRENT_PARENT_DIRECTORY}/${CURRENT_FILENAME}:${CMAKE_CURRENT_LIST_LINE} >> ${msg}${lsd_slam_COLOR_RESET}")
endmacro(lsd_slam_print_status_colorized)

# To print nice message with information about the source file
# Output: file_name:: message
macro(lsd_slam_print_status msg)
  get_filename_component(CURRENT_FILENAME "${CMAKE_CURRENT_LIST_FILE}" NAME)
  get_filename_component(CURRENT_PATH "${CMAKE_CURRENT_LIST_FILE}" PATH)
  get_filename_component(CURRENT_PARENT_DIRECTORY "${CURRENT_PATH}" NAME)
  if(NOT ARGN)
    message(STATUS "${lsd_slam_COLOR_GREEN}${CURRENT_PARENT_DIRECTORY}/${CURRENT_FILENAME}:${CMAKE_CURRENT_LIST_LINE} >> ${msg}${ARGN}${lsd_slam_COLOR_RESET}")
  else()
    message(STATUS "${lsd_slam_COLOR_GREEN}${CURRENT_PARENT_DIRECTORY}/${CURRENT_FILENAME}:${CMAKE_CURRENT_LIST_LINE} >> \n${lsd_slam_COLOR_RESET}")
    list(APPEND msg ${ARGN})
    foreach(m in ${msg})
      message(STATUS "${lsd_slam_COLOR_GREEN}${m}${lsd_slam_COLOR_RESET}")
    endforeach()
endif()
endmacro(lsd_slam_print_status)

# To print nice error message with information about the source file
macro(lsd_slam_print_error msg) # TODO: improve this for ARGN
  get_filename_component(CURRENT_FILENAME "${CMAKE_CURRENT_LIST_FILE}" NAME)
  get_filename_component(CURRENT_PATH "${CMAKE_CURRENT_LIST_FILE}" PATH)
  get_filename_component(CURRENT_PARENT_DIRECTORY "${CURRENT_PATH}" NAME)
  message(FATAL_ERROR "${lsd_slam_COLOR_RED}${CURRENT_PARENT_DIRECTORY}/${CURRENT_FILENAME}:${CMAKE_CURRENT_LIST_LINE} >> ${msg}${ARGN}${lsd_slam_COLOR_RESET}")
endmacro(lsd_slam_print_error)

# Contains common (useful) cmake macros or routines ============================
# useful routine for building a binary
# requires ${ALL_LIBRARRIES}
macro(lsd_slam_add_executable target)
  set(srcs ${target}.cc ${ARGN})
  add_executable(${target} ${srcs})
  if(ALL_LIBRARIES)
    add_dependencies(${target} ${ALL_LIBRARIES})
    target_link_libraries(${target} ${ALL_LIBRARIES})
  endif(ALL_LIBRARIES)
endmacro(lsd_slam_add_executable)

# add a test
macro(lsd_slam_add_test target)
  lsd_slam_add_executable(${target} ${ARGN})
  add_test(${target} ${CMAKE_CURRENT_BINARY_DIR}/${target})
endmacro(lsd_slam_add_test)

# commong build settings (mostly to deal with Windows )
macro(lsd_slam_common_build_setting)
  if(CMAKE_SYSTEM_PROCESSOR MATCHES "^arm")
    option(LsdSlam_ENABLE_NEON "Enable NEON" ON)
    if(LsdSlam_ENABLE_NEON)
      add_definitions(-DENABLE_NEON)  # enable NEON code for ARM
    endif()
  else()
    option(LsdSlam_ENABLE_SSE "Enable SSE" ON)
    if(LsdSlam_ENABLE_SSE)
      add_definitions(-DENABLE_SSE)   # SSE code
    endif()
    set(CMAKE_CXX_FLAGS_RELEASE ${CMAKE_CXX_FLAGS_RELEASE} "${SSE_FLAGS}")
    set(CMAKE_CXX_FLAGS_RELWITHDEBINFO ${CMAKE_CXX_FLAGS_RELWITHDEBINFO} "${SSE_FLAGS}")
  endif()

  if(WIN32)
    add_definitions(-DNOMINMAX)  # resolve conflicts of std::min()/std::max() on Windows MSVC
    add_definitions(-D_USE_MATH_DEFINES)
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-DEIGEN_DONT_ALIGN_STATICALLY)  # this is unusual
    add_definitions(-D_CRT_SECURE_NO_WARNINGS)
    add_definitions(-DWIN32_LEAN_AND_MEAN) # speed up compiler by omitting some headers
    add_definitions(-DM_SQRT1_2=0.707106781186547524401) # missing in MSVC2013
    add_definitions(-DM_PI=3.14159265358979323846) # missing in MSVC2013
    add_definitions("/MP") # multiple processes compilation

    # some magical optimized code flags
    #add_definitions("/GR-")  # disable runtime type info
    add_definitions("/fp:fast")  # fast floating point calc.
    #add_definitions("/GS-")  # disable security check
    add_definitions("/W0")  # disable all warnings
    #add_definitions("/GL")  # enable whole program optimization

    if(BUILD_SHARED_LIBS)
      # disable warning on missing DLL interfaces
      add_definitions("/wd4251")
    endif()

    set(CMAKE_CXX_FLAGS_RELEASE ${CMAKE_CXX_FLAGS_RELEASE}  " /D_SECURE_SCL=0 -march=native")
    set(CMAKE_CXX_FLAGS_RELWITHDEBINFO ${CMAKE_CXX_FLAGS_RELWITHDEBINFO} " /D_SECURE_SCL=0 -march=native")
  else(WIN32)
    if(NOT CMAKE_BUILD_TYPE STREQUAL Debug)
      # SSE is not supported on ARM!
      if(CMAKE_SYSTEM_PROCESSOR MATCHES "^arm")
        add_definitions(-mfpu=neon -mfloat-abi=softfp -march=armv7-a)  # vectorization for ARM
      else()
        add_definitions(-march=native)
      endif()
    endif()
  endif(WIN32)
endmacro(lsd_slam_common_build_setting)
