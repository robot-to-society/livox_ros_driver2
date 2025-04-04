import launch
import launch.actions
import launch.substitutions
import launch_ros.actions

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import TimerAction
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource, FrontendLaunchDescriptionSource

import os

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    livox_dir = get_package_share_directory('livox_ros_driver2')
    cartographer_config_dir = LaunchConfiguration('cartographer_config_dir', 
                                                    default=os.path.join(livox_dir, 'config'))
    configuration_basename = LaunchConfiguration('configuration_basename', default='cartographer_3d.lua')

    resolution = LaunchConfiguration('resolution', default='0.05')
    publish_period_sec = LaunchConfiguration('publish_period_sec', default='0.5')

    return LaunchDescription([
        SetEnvironmentVariable('RCUTILS_CONSOLE_OUTPUT_FORMAT', '[{severity}] {message}'),
        SetEnvironmentVariable('RCUTILS_CONSOLE_STDOUT_LINE_BUFFERED', '1'),
        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),
        SetEnvironmentVariable('RCUTILS_LOGGING_MIN_SEVERITY', 'ERROR'),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=['-0.05', '0.0', '0.15', '0.0', '0.0', '0.0', 'base_link', 'livox_frame']
            ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=['-0.08', '0.05', '0.0', '0.0', '0.0', '0.0', 'base_link', 'imu_link']
            ),
        Node(
	    package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'map', 'base_link']
            ),
        Node(
            ## Configure the TF of the robot to the origin of the map coordinates
            # map TF to odom TF
            package='tf2_ros',
            executable='static_transform_publisher',
            namespace='',
            output='screen',
            arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', 'map', 'odom']
        ),

        TimerAction(
		period=5.0,
                actions=[
        Node(
            package='cartographer_ros',
            executable='cartographer_node',
            output='log',
            parameters=[
                {'use_sim_time': use_sim_time},
            ],
            arguments=['-configuration_directory', cartographer_config_dir, '-configuration_basename', configuration_basename],
            remappings=[
                ('imu','/livox/imu'),
                ('points2','/livox/lidar'),
            ]
        ),
        DeclareLaunchArgument(
            'resolution',
            default_value=resolution,
            description='Resolution of a grid cell in the published occupancy grid'),

        DeclareLaunchArgument(
            'publish_period_sec',
            default_value=publish_period_sec,
            description='OccupancyGrid publishing period'),

        Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            name='occupancy_grid_node',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-resolution', resolution, '-publish_period_sec', publish_period_sec])
        ]),

        # Octomap server
        Node(
            package='octomap_server',
            executable='octomap_server_node',
            name='octomap_server',
            parameters=[{
	        'pointcloud_topic': '/scan_matched_points2',
                'frame_id': 'map',
                'resolution': 0.05,
                'sensor.model.max_range': 20.0,
                'latch': True
            }],
            remappings=[
                ('cloud_in','/scan_matched_points2'),
            ]
        ),

	# Robot pose publisher
	Node(
	    package='robot_pose_publisher_ros2',
	    executable='robot_pose_publisher',
	    name='robot_pose_publisher',
	    output='screen',
	    parameters=[
		{'use_sim_time': use_sim_time},
		{'is_stamped': True},
		{'map_frame': 'map'},
		{'base_frame': 'base_link'}
	    ],
            remappings=[
                ('robot_pose','/mavros/vision_pose/pose')
            ]
	),
            
    ])

