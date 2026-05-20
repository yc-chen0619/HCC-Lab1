import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import os

class TelloPhotoTaker(Node):
    def __init__(self):
        super().__init__('tello_photo_taker')
        
        # 訂閱 tello_ros 的影像話題 (請確認你的 tello_ros 發布的話題名稱，通常是 /image_raw 或 /tello/image_raw)
        self.subscription = self.create_subscription(
            Image,
            '/image_raw',  
            self.listener_callback,
            10
        )
        self.bridge = CvBridge()
        self.photo_id = 0
        
        # 確保照片資料夾存在
        if not os.path.exists('photos'):
            os.makedirs('photos')

        self.get_logger().info("\n===================================="
                               "\nROS 2 棋盤格拍照節點已啟動！"
                               "\n請點擊 OpenCV 視窗，並使用以下按鍵："
                               "\n按下 'k' : 拍攝照片並存檔"
                               "\n按下 'q' : 關閉程式"
                               "\n====================================")

    def listener_callback(self, msg):
        try:
            # 將 ROS 2 Image 轉為 OpenCV BGR 格式
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # 顯示影像
            cv2.imshow("ROS2 Tello Camera", cv_image)
            
            # 監聽鍵盤
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('k'):
                filename = f"photos/photo_{self.photo_id:03d}.jpg"
                cv2.imwrite(filename, cv_image)
                self.get_logger().info(f"成功儲存照片: {filename}")
                self.photo_id += 1
                
            elif key == ord('q'):
                self.get_logger().info("正在關閉拍照節點...")
                cv2.destroyAllWindows()
                rclpy.shutdown()
                
        except Exception as e:
            self.get_logger().error(f"影像處理失敗: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = TelloPhotoTaker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        cv2.destroyAllWindows()
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()