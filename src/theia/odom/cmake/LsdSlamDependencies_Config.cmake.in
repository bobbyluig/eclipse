include(LsdSlamUtil)
lsd_slam_print_status("Setup paths for dependencies")
set(msg 
  "\n"
  "BEGIN NOTEs for dependencies configuration =================================\n"
  "You can configure dependencies in a single config file (${CMAKE_CURRENT_BINARY_DIR}/LsdSlamDependencies_Config.cmake \n"
  "There are sample configuration paths in the file\n"
  "To use this config file, change to LsdSlam_USE_MANUAL_CONFIG_FILE to TRUE\n"
  "END NOTEs for dependencies configuration ===================================\n"
)

lsd_slam_print_status(${msg})

option(LsdSlam_USE_MANUAL_CONFIG_FILE "To use manual config file (LsdSlamDependencies_Config.cmake)" ON)

if(LsdSlam_USE_MANUAL_CONFIG_FILE)  # set to ON here to manually configure
  ## Required dependencies =======================================================
  # Boost
  set(BOOST_ROOT C:/Users/Thanh/deps_android/boost_1_55_0)
  if(WIN32)
    set(Boost_NAMESPACE libboost)  # windows build needs this ??
  endif()
  if(ANDROID)
    set(Boost_INCLUDE_DIR C:/Users/Thanh/deps_android/boost_1_55_0)
    set(Boost_LIBRARY_DIR ${BOOST_ROOT}/stage/lib)
    set(Boost_INCLUDE_DIRS ${Boost_INCLUDE_DIR})
    set(Boost_ATOMIC_LIBRARY_RELEASE ${BOOST_LIBRARYDIR}/libboost_atomic-gcc-mt-s-1_55.a)
    set(Boost_THREAD_LIBRARY_RELEASE ${BOOST_LIBRARYDIR}/libboost_thread_pthread-gcc-mt-s-1_55.a)
    set(Boost_SYSTEM_LIBRARY_RELEASE ${BOOST_LIBRARYDIR}/libboost_system-gcc-mt-s-1_55.a)
    set(Boost_LIBRARIES ${Boost_ATOMIC_LIBRARY_RELEASE}
      ${Boost_THREAD_LIBRARY_RELEASE} ${Boost_SYSTEM_LIBRARY_RELEASE})
  endif(ANDROID)
  lsd_slam_print_status("Boost_INCLUDE_DIR:${Boost_INCLUDE_DIR}")

  # OpenCV
  set(OpenCV_STATIC OFF)
  set(OpenCV_DIR D:/dev/gitlab_structural_modeling/precompiled/x86/vc12/prebuilts/opencv)
  lsd_slam_print_status("OpenCV_DIR:${OpenCV_DIR}")

  # G2O
  set(G2O_ROOT C:/Users/Thanh/deps_android/gcc4.8-arm-abiv7a-api18-32bit/g2o)
  if(ANDROID)
    set(G2O_INCLUDE_DIR ${G2O_ROOT}/include "${G2O_ROOT}/include/EXTERNAL/csparse")
    set(G2O_CORE_LIBRARY ${G2O_ROOT}/lib/libg2o_core.so)
    set(G2O_STUFF_LIBRARY ${G2O_ROOT}/lib/libg2o_stuff.so)
    set(G2O_SOLVER_DENSE ${G2O_ROOT}/lib/libg2o_solver_dense.so)
    set(G2O_TYPES_SLAM3D ${G2O_ROOT}/lib/libg2o_types_slam3d.so)
    set(G2O_SIMULATOR ${G2O_ROOT}/lib/libg2o_simulator.so)

    # csparse
    set(G2O_SOLVER_CSPARSE ${G2O_ROOT}/lib/libg2o_solver_csparse.so)
    set(G2O_SOLVER_CSPARSE_EXTENSION ${G2O_ROOT}/lib/libg2o_csparse_extension.so)
    set(G2O_EXT_CSPARSE ${G2O_ROOT}/lib/libg2o_ext_csparse.so)

    # eigen
    set(G2O_SOLVER_EIGEN ${G2O_ROOT}/lib/libg2o_solver_eigen.so)
  endif()


  ## Optional dependencies =======================================================
  #OpenGL
  if(ANDROID)
    set(OPENGL_INCLUDE_DIR "")
    set(OPENGL_LIBRARIES libEGL.so libGLESv1_CM.so libGLESv2.so)
    set(OPENGL_FOUND TRUE)
  endif()

  # Freeglut
  set(GLUT_INCLUDE_DIR D:/deps_msvc_common/freeglut-2.8.1/include)
  #set(GLUT_glut_LIBRARY D:/deps_msvc_common/freeglut-2.8.1/lib/x86/freeglut.lib)
  set(GLUT_BINARY_DIR "${GLUT_INCLUDE_DIR}/../lib/x86")
  if(ANDROID)
    set(GLUT_FOUND TRUE)
    set(GLUT_LIBRARIES C:/Users/Thanh/deps_android/freeglut3-android-modules/install_in_ndk/sysroot/usr/lib/freeglut-gles.a)
  endif()
  lsd_slam_print_status("GLUT_INCLUDE_DIR:${GLUT_INCLUDE_DIR}")

  # GLEW
  set(GLEW_INCLUDE_DIR D:/deps_msvc_common/glew-1.10.0/include)
  #set(GLEW_LIBRARY D:/deps_msvc_common/glew-1.10.0/lib/Release/Win32/glew32.lib)
  set(GLEW_BINARY_DIR ${GLEW_INCLUDE_DIR}/../bin/Release/Win32)
  lsd_slam_print_status("GLEW_INCLUDE_DIR:${GLEW_INCLUDE_DIR}")


endif()
