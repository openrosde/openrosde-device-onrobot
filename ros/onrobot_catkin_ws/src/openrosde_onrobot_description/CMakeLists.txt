cmake_minimum_required(VERSION 2.8.3)
project(openrosde_onrobot_description)

find_package(catkin REQUIRED)

catkin_package()

# Install the robot description files.
install(DIRECTORY urdf
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
