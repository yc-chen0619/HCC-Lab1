import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
from pupil_apriltags import Detector
from geometry_msgs.msg import PoseStamped
from builtin_interfaces.msg import Time
from rclpy.qos import QoSProfile
import math
from apriltag_detector_pkg.tag_pose_loader import load_tag_poses
from ament_index_python.packages import get_package_share_directory
import os
from scipy.spatial.transform import Rotation as R

class ImageSubscriber(Node):
    def __init__(self):
        super().__init__('image_subscriber')
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',
            self.listener_callback,
            10
        )
        self.bridge = CvBridge()

        # Initialize AprilTag detector
        self.detector = Detector(
            families='tag36h11',
            nthreads=1,
            quad_decimate=1.0,
            quad_sigma=0.0,
            refine_edges=1,
            decode_sharpening=0.25,
            debug=0
        )

        self.get_logger().info("Image subscriber with pupil_apriltags initialized.")

        # Add publisher
        self.pose_pub = self.create_publisher(PoseStamped, '/drone_pose', 10)

        # === Camera intrinsics === (You must adjust based on your Tello's camera)
        self.fx = 911.00816  # Focal length x
        self.fy = 909.73315  # Focal length y
        self.cx = 493.744  # Principal point x (image center)
        self.cy = 360.485  # Principal point y

        # Tag size in meters
        self.tag_size = 0.159  # Size of the AprilTag in meters

        self.get_logger().info("Pose publisher Initialized.")

        # === Load AprilTag world poses from YAML ===
        package_share = get_package_share_directory('apriltag_detector_pkg')
        yaml_path = os.path.join(package_share, 'map', 'apriltag_map.yaml')
        self.tag_poses = load_tag_poses(yaml_path)
        self.tag_pose_dict = {tag['id']: tag for tag in self.tag_poses}

    def get_tag_world_pose(self, tag_id):
        """
        Returns a 4x4 transformation matrix T_tag_in_world from YAML.
        """
        tag = self.tag_pose_dict.get(tag_id)
        if tag is None:
            self.get_logger().warn(f"No world pose defined for tag ID {tag_id}")
            return None

        pos = tag['position']
        rpy = tag['orientation_rpy']
        rot = R.from_euler('xyz', rpy).as_matrix()

        T = np.eye(4)
        T[:3, :3] = rot
        T[:3, 3] = pos
        return T

    def listener_callback(self, msg):
        try:

            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)

            results = self.detector.detect(
                gray,
                estimate_tag_pose=True,
                camera_params=(self.fx, self.fy, self.cx, self.cy),
                tag_size=self.tag_size
            )

            # Process result if needed

            self.get_logger().info(f"Detected {len(results)} AprilTags")

            for r in results:
                corners = np.array(r.corners, dtype=np.int32).reshape((-1, 1, 2))
                cv2.polylines(cv_image, [corners], isClosed=True, color=(0, 255, 0), thickness=2)

                center = (int(r.center[0]), int(r.center[1]))
                cv2.circle(cv_image, center, 4, (0, 0, 255), -1)
                cv2.putText(cv_image, f"ID: {r.tag_id}", (center[0] + 10, center[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
                if r.pose_t is None or r.pose_R is None:
                    self.get_logger().warn(f"AprilTag {r.tag_id} detected, but pose not available.")
                    continue

                # Estimate pose from detection
                pose_R, pose_t = r.pose_R, r.pose_t  # rotation (3x3) and translation (3x1) matrices
                self.get_logger().info(f"R: {pose_R}, t: {pose_t}")

                # Get T_tag_in_cam from detection
                T_tag_in_cam = np.eye(4)
                T_tag_in_cam[:3, :3] = pose_R
                T_tag_in_cam[:3, 3] = pose_t.flatten()

                # Get known T_tag_in_world
                T_tag_in_world = self.get_tag_world_pose(r.tag_id)
                if T_tag_in_world is None:
                    continue

                # Compute T_cam_in_world
                T_cam_in_tag = np.linalg.inv(T_tag_in_cam)
                T_cam_in_world = T_tag_in_world @ T_cam_in_tag

                # Publish T_cam_in_world as drone pose
                pose_msg = PoseStamped()
                pose_msg.header.stamp = msg.header.stamp
                pose_msg.header.frame_id = "map"

                pos = T_cam_in_world[:3, 3]
                quat = R.from_matrix(T_cam_in_world[:3, :3]).as_quat()

                pose_msg.pose.position.x = float(pos[0])
                pose_msg.pose.position.y = float(pos[1])
                pose_msg.pose.position.z = float(pos[2])
                pose_msg.pose.orientation.x = float(quat[0])
                pose_msg.pose.orientation.y = float(quat[1])
                pose_msg.pose.orientation.z = float(quat[2])
                pose_msg.pose.orientation.w = float(quat[3])

                self.pose_pub.publish(pose_msg)


            cv2.imshow("AprilTag Detection", cv_image)
            cv2.waitKey(1)

        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = ImageSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

from scipy.spatial.transform import Rotation as R

def rotation_matrix_to_quaternion(rot_matrix):
    r = R.from_matrix(rot_matrix)
    return r.as_quat()  # Returns [x, y, z, w]
