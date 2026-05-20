from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='apriltag_detector_pkg',
            executable='image_subscriber',
            name='apriltag_detector',
            output='screen'
        ),
        Node(
            package='apriltag_detector_pkg',
            executable='apriltag_visualizer',
            name='apriltag_visualizer',
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', './src/apriltag_detector_pkg/rviz/config.rviz']
        )
    ])