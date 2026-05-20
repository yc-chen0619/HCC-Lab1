# HCC-Lab1 (apriltag_detector_pkg)

`apriltag_detector_pkg` is a ROS 2 package that subscribes to an image topic (`/image_raw`), detects AprilTags using the `pupil_apriltags` Python package, and processes the images accordingly. This package is intended to be used in a robotics system that requires real-time AprilTag detection for localization, mapping, or other tasks.

## Features
- Subscribes to the `/image_raw` topic of type `sensor_msgs/Image`.
- Converts the raw image message to a format suitable for OpenCV.
- Detects AprilTags in the image using `pupil_apriltags`.
- Visualizes the results by overlaying detected AprilTags on the received image.

## Install additional Python dependencies
```bash
$pip install pupil-apriltags opencv-python
```

## Build the Workspace
```bash
$ cd ~/tello_ros_ws/
$ colcon build --packages-select apriltag_detector_pkg
```

## Source the Workspace
```bash
$ source ~/tello_ros_ws/install/setup.bash
```

1. ## Run the node to take photo
  ```bash
  $ ros2 launch tello_driver teleop_launch.py
  $ ros2 run apriltag_detector_pkg take_photo
  ```

2. ## Find camera intrinsic matrix
  use ``` camera_calibration.py ``` to get  camera intrinsic matrix.

3. ## Run the node to localization in Rviz by using AprilTag
  you need to open ``` image_subscriber.py ``` and modify the camera intrinsic parameter. and then.
  ```bash
  $ cd ~/tello_ros_ws/
  $ colcon build --packages-select apriltag_detector_pkg
  $ ros2 launch tello_driver teleop_launch.py
  $ ros2 run apriltag_detector_pkg apriltag_tracker_launch.py
  ```
