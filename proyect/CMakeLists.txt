cmake_minimum_required(VERSION 3.0.2)
project(proyect)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  geometry_msgs
  nav_msgs
  std_srvs
  message_generation
)

add_message_files(
  FILES
  LevelInfo.msg
  Collectible.msg
  CollectibleArray.msg
  Enemy.msg
  EnemyArray.msg
  Projectile.msg
  ProjectileArray.msg
  MazeLayout.msg
)

add_service_files(
  FILES
  LoadLevel.srv
  GetScore.srv
)

generate_messages(
  DEPENDENCIES
  std_msgs
  geometry_msgs
  nav_msgs
)

catkin_package(
  CATKIN_DEPENDS 
    rospy 
    std_msgs 
    geometry_msgs 
    nav_msgs
    std_srvs
    message_runtime
)

include_directories(
  ${catkin_INCLUDE_DIRS}
)

catkin_install_python(PROGRAMS
  scripts/game_manager_node.py
  scripts/maze_generator_node.py
  scripts/player_node.py
  scripts/input_node.py
  scripts/collectibles_node.py
  scripts/enemies_node.py
  scripts/projectiles_node.py
  scripts/collision_node.py
  scripts/score_node.py
  scripts/renderer_node.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)