cmake_minimum_required(VERSION 3.15)
project(SlopeExample CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Eigen3 REQUIRED)
find_package(slope REQUIRED)

add_executable(slope-example example.cpp)
target_link_libraries(slope-example PRIVATE slope::slope Eigen3::Eigen)

install(TARGETS slope-example DESTINATION bin)
