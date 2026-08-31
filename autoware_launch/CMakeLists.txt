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

install(CODE
  "set(_link \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}/config\")
   if(NOT EXISTS \"\${_link}\" AND NOT IS_SYMLINK \"\${_link}\")
     execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink config_lv4 \"\${_link}\")
   endif()"
)

ament_auto_package(
  INSTALL_TO_SHARE
  launch
  rviz
)
