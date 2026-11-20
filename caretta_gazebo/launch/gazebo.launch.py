"""Caretta in Gazebo (Ignition Fortress) with ros2_control diff_drive_controller, LiDAR and camera.

ros2 launch caretta_gazebo gazebo.launch.py              (add rviz:=true to see robot + /scan)
headless: ros2 launch caretta_gazebo gazebo.launch.py extra_gz_args:="-s --headless-rendering"
drive: ros2 run teleop_twist_keyboard teleop_twist_keyboard \
         --ros-args -r cmd_vel:=/diff_drive_controller/cmd_vel_unstamped
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (AppendEnvironmentVariable, DeclareLaunchArgument,
                            IncludeLaunchDescription, RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_share = get_package_share_directory('caretta_description')
    xacro_path = os.path.join(description_share, 'urdf', 'caretta.urdf.xacro')
    gazebo_share = get_package_share_directory('caretta_gazebo')

    world = LaunchConfiguration('world')
    gz_args = [LaunchConfiguration('extra_gz_args'), ' -r ', world]

    # Gazebo resolves package://caretta_description/... meshes from this path
    resource_path = AppendEnvironmentVariable(
        'IGN_GAZEBO_RESOURCE_PATH', os.path.dirname(description_share)
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': gz_args}.items(),
    )

    robot_description = ParameterValue(
        Command(['xacro ', xacro_path, ' use_gazebo:=true']), value_type=str
    )

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}],
        output='screen',
    )

    # Gazebo -> ROS: /clock (needed for use_sim_time), LiDAR /scan, camera info
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[ignition.msgs.LaserScan',
            '/camera/camera_info@sensor_msgs/msg/CameraInfo[ignition.msgs.CameraInfo',
        ],
        output='screen',
    )

    # camera image via ros_gz_image (more efficient than parameter_bridge for images)
    image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],
        output='screen',
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(gazebo_share, 'rviz', 'sim.rviz')],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'caretta', '-z', '0.005'],
        output='screen',
    )

    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    diff_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller'],
        output='screen',
    )

    return LaunchDescription([
        DeclareLaunchArgument('world', default_value=os.path.join(gazebo_share, 'worlds', 'caretta_test.sdf'),
                              description='SDF world (must load the Sensors system for the LiDAR)'),
        DeclareLaunchArgument('extra_gz_args', default_value='',
                              description='extra Gazebo args, e.g. "-s --headless-rendering"'),
        DeclareLaunchArgument('rviz', default_value='false', description='start RViz with robot + scan'),
        resource_path,
        gazebo,
        robot_state_publisher,
        bridge,
        image_bridge,
        rviz,
        spawn_robot,
        # controllers can only start after the robot (and its controller_manager) exists
        RegisterEventHandler(OnProcessExit(
            target_action=spawn_robot,
            on_exit=[joint_state_broadcaster, diff_drive_controller],
        )),
    ])
