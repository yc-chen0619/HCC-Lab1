import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import math

class StaticTagPublisher(Node):
    def __init__(self):
        super().__init__('static_tag_tf_broadcaster')
        self.br = TransformBroadcaster(self)

        self.timer = self.create_timer(1.0, self.broadcast_tag_tf)

    def broadcast_tag_tf(self):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'map'
        t.child_frame_id = 'tag_0'

        # Define position of the tag
        t.transform.translation.x = 0.0
        t.transform.translation.y = 0.0
        t.transform.translation.z = 1.5

        # Define rotation as quaternion (no rotation = identity)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.707
        t.transform.rotation.z = 0.0
        t.transform.rotation.w = 0.707

        self.br.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = StaticTagPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
