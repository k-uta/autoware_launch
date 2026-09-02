cmake_minimum_required(VERSION 3.5)
project(autoware_launch)

find_package(ament_cmake_auto REQUIRED)
ament_auto_find_build_dependencies()

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

install(DIRECTORY config/ DESTINATION share/${PROJECT_NAME}/config_lv4)
install(DIRECTORY config_lv2 DESTINATION share/${PROJECT_NAME})

install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}_levels/launch_lv4)
install(DIRECTORY launch_lv2 DESTINATION share/${PROJECT_NAME}_levels)

install(PROGRAMS
  scripts/switch_autonomy_level.sh
  scripts/show_autonomy_level.sh
  DESTINATION lib/${PROJECT_NAME}
)

install(CODE
  "execute_process(
     COMMAND bash ${CMAKE_CURRENT_SOURCE_DIR}/scripts/switch_autonomy_level.sh
             --init lv4
             --share-dir \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}\"
     RESULT_VARIABLE _rc)
   if(NOT _rc EQUAL 0)
     message(FATAL_ERROR \"failed to initialize the autonomy level (rc=\${_rc})\")
   endif()"
)

ament_auto_package(
  INSTALL_TO_SHARE
  rviz
)
