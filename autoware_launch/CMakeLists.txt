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

install(DIRECTORY launch/ DESTINATION share/${PROJECT_NAME}_levels/launch_lv4)
install(DIRECTORY launch_lv2 DESTINATION share/${PROJECT_NAME}_levels)

install(CODE
  "set(_share \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}\")
   set(_levels \"\$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/share/${PROJECT_NAME}_levels\")
   set(_level lv4)
   get_filename_component(_config_target \"\${_share}/config\" REALPATH)
   if(_config_target MATCHES \"config_(lv[0-9]+)\$\")
     set(_level \"\${CMAKE_MATCH_1}\")
   endif()
   set(_src \"\${_levels}/launch_\${_level}\")
   file(REMOVE_RECURSE \"\${_share}/launch\")
   file(GLOB_RECURSE _rel_paths LIST_DIRECTORIES false RELATIVE \"\${_src}\" \"\${_src}/*\")
   foreach(_rel IN LISTS _rel_paths)
     get_filename_component(_dir \"\${_share}/launch/\${_rel}\" DIRECTORY)
     file(MAKE_DIRECTORY \"\${_dir}\")
     file(RELATIVE_PATH _target \"\${_dir}\" \"\${_src}/\${_rel}\")
     execute_process(COMMAND \${CMAKE_COMMAND} -E create_symlink \"\${_target}\" \"\${_share}/launch/\${_rel}\")
   endforeach()"
)

ament_auto_package(
  INSTALL_TO_SHARE
  rviz
)
