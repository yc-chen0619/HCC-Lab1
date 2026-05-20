import os
from glob import glob
from setuptools import setup

package_name = 'apriltag_detector_pkg'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'resource'), ['resource/apriltag_detector_pkg']),
        ('share/apriltag_detector_pkg/map', ['map/apriltag_map.yaml']),
    ],
    install_requires=['setuptools', 'pupil-apriltags', 'opencv-python'],
    zip_safe=True,
    maintainer='Your Name',
    maintainer_email='your_email@example.com',
    description='Detect AprilTags from a camera stream using pupil_apriltags.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'image_subscriber = apriltag_detector_pkg.image_subscriber:main',
            'apriltag_visualizer = apriltag_detector_pkg.apriltag_visualizer:main',
            'take_photo = apriltag_detector_pkg.take_photo:main',
        ],
    },
)
