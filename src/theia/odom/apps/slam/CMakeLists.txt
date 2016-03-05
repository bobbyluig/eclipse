cmake_minimum_required(VERSION 2.8.9)
project(slam_app)

## demos
#add_executable(main_on_images main_on_images.cc)
#set_property(TARGET main_on_images PROPERTY FOLDER "lsd_slam/apps")
#target_link_libraries(main_on_images ${ALL_LIBRARIES} ${OpenCV_LIBRARIES} "C:/projects/uni/dissertation/Libraries/icg_lsd_slam/lsd-slam/lib/lsd_slam.lib")

#add_executable(main_live_odometry main_live_odometry.cc)
#set_property(TARGET main_live_odometry PROPERTY FOLDER "lsd_slam/apps")
#target_link_libraries(main_live_odometry ${ALL_LIBRARIES} ${OpenCV_LIBRARIES} "C:/projects/uni/dissertation/Libraries/icg_lsd_slam/lsd-slam/lib/lsd_slam.lib")

## only this works at the moment
add_executable(sample_app sample_app.cc DebugOutput3DWrapper.cpp DebugOutput3DWrapper.h)
set_property(TARGET sample_app PROPERTY FOLDER "lsd_slam/apps")

# set(LIB_CXSPARSE  /usr/lib/x86_64-linux-gnu/libcxsparse.so)

target_link_libraries(sample_app ${LsdSlam_ALL_LIBRARIES} ${LIB_CXSPARSE})

lsd_slam_print_status("LsdSlam_ALL_LIBRARIES:${LsdSlam_ALL_LIBRARIES}")
