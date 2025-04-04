from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pointcloud_to_laserscan', executable='pointcloud_to_laserscan_node',
            remappings=[('cloud_in', '/cloud_registered_body'),
                        ('scan', '/ap/laserscan')],
            parameters=[{
                'target_frame': 'body',
                'transform_tolerance': 0.01,
                'min_height': 0.0,
                'max_height': 0.2,
                'angle_min': -3.1415,  # - M_PI
                'angle_max': 3.1415,  # M_PI
                'angle_increment': 0.0873,  # 5 degree
                'scan_time': 0.1,# 10Hz
                'range_min': 0.2, # 20cm
                'range_max': 5.0, # 5m
                'use_inf': True,
                'inf_epsilon': 1.0
            }],
            name='pointcloud_to_laserscan'
        )
    ])

