cmake_minimum_required(VERSION 2.8.3)
project(openrosde_onrobot_launch)

find_package(catkin REQUIRED)

catkin_package()

catkin_install_python(
  PROGRAMS
    scripts/onrobot_rg_command_bridge.py
    scripts/onrobot_rg_gripper_action.py
    scripts/onrobot_rg_joint_states.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

# Install the launch files.
install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
