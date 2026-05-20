import rclpy
from rclpy.node import Node
from visualization_msgs.msg import Marker
from std_msgs.msg import Header, ColorRGBA
from apriltag_detector_pkg.tag_pose_loader import load_tag_poses
from ament_index_python.packages import get_package_share_directory
import os
from scipy.spatial.transform import Rotation as R

package_share = get_package_share_directory('apriltag_detector_pkg')
yaml_path = os.path.join(package_share, 'map', 'apriltag_map.yaml')
tag_poses = load_tag_poses(yaml_path)

class AprilTagVisualizer(Node):
    def __init__(self):
        super().__init__('apriltag_visualizer')
        self.publisher = self.create_publisher(Marker, 'apriltag_marker', 10)
        self.timer = self.create_timer(1.0, self.publish_markers)
        self.tag_poses = tag_poses

    def publish_markers(self):
        for tag in self.tag_poses:
            marker = Marker()
            marker.header = Header()
            marker.header.frame_id = 'map'
            marker.header.stamp = self.get_clock().now().to_msg()

            marker.ns = 'apriltag'
            marker.id = tag['id']
            marker.type = Marker.CUBE
            marker.action = Marker.ADD

            # Position
            marker.pose.position.x = tag['position'][0]
            marker.pose.position.y = tag['position'][1]
            marker.pose.position.z = tag['position'][2]

            # Orientation (convert RPY to quaternion)
            quat = R.from_euler('xyz', tag['orientation_rpy']).as_quat()
            marker.pose.orientation.x = quat[0]
            marker.pose.orientation.y = quat[1]
            marker.pose.orientation.z = quat[2]
            marker.pose.orientation.w = quat[3]

            # Size
            marker.scale.x = 0.16
            marker.scale.y = 0.16
            marker.scale.z = 0.01

            # Color
            marker.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)

            self.publisher.publish(marker)

            # Add text marker for tag ID 
            text_marker = Marker()
            text_marker.header = marker.header
            text_marker.ns = 'apriltag_text'
            text_marker.id = tag['id']
            text_marker.type = Marker.TEXT_VIEW_FACING
            text_marker.action = Marker.ADD

            # Position the text slightly above the tag
            text_marker.pose.position.x = tag['position'][0]
            text_marker.pose.position.y = tag['position'][1]
            text_marker.pose.position.z = tag['position'][2] + 0.1  # Adjust as needed

            text_marker.pose.orientation.x = 0.0
            text_marker.pose.orientation.y = 0.0
            text_marker.pose.orientation.z = 0.0
            text_marker.pose.orientation.w = 1.0

            text_marker.scale.z = 0.1  # Height of the text

            text_marker.color = ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0)  # Red text

            text_marker.text = str(tag['id'])

            self.publisher.publish(text_marker)

def main(args=None):
    rclpy.init(args=args)
    node = AprilTagVisualizer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()