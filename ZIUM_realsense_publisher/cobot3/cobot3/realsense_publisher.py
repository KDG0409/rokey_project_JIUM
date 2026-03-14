import rclpy
from rclpy.node import Node
import pyrealsense2 as rs
import numpy as np
from sensor_msgs.msg import Image, CameraInfo
        
class RealsensePublisher(Node):
    def __init__(self):
        super().__init__('realsense_pub_node', namespace='dsr01')
        
        # [발행자 설정] 기존 소스코드의 토픽 이름과 형식을 맞춤
        self.color_pub = self.create_publisher(Image, 'camera/color/image_raw', 10)
        self.depth_pub = self.create_publisher(Image, 'camera/aligned_depth_to_color/image_raw', 10)
        self.info_pub = self.create_publisher(CameraInfo, 'camera/color/camera_info', 10)

        # RealSense 파이프라인 설정
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        # 시작 및 정렬 설정 (Color 기준)
        self.profile = self.pipeline.start(config)
        self.align = rs.align(rs.stream.color)
        
        # 카메라 내부 파라미터(K) 미리 로드
        self.intrinsics = self.profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
        self.info_msg = self.get_camera_info()

        # 주기적으로 발행 (30Hz)
        self.timer = self.create_timer(1.0/30, self.timer_callback)
        self.get_logger().info("RealSense Publisher Node started (dsr01)")

    def get_camera_info(self):
        """CameraInfo 메시지 초기화"""
        info = CameraInfo()
        info.header.frame_id = 'camera_color_optical_frame'
        info.width = self.intrinsics.width
        info.height = self.intrinsics.height
        info.distortion_model = 'plumb_bob'
        info.d = [float(x) for x in self.intrinsics.coeffs]
        info.k = [
            float(self.intrinsics.fx), 0.0, float(self.intrinsics.ppx),
            0.0, float(self.intrinsics.fy), float(self.intrinsics.ppy),
            0.0, 0.0, 1.0
        ]
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        info.p = [
            float(self.intrinsics.fx), 0.0, float(self.intrinsics.ppx), 0.0,
            0.0, float(self.intrinsics.fy), float(self.intrinsics.ppy), 0.0,
            0.0, 0.0, 1.0, 0.0
        ]
        return info

    def timer_callback(self):
        try:
            frames = self.pipeline.wait_for_frames()
            aligned_frames = self.align.process(frames)
            
            color_frame = aligned_frames.get_color_frame()
            depth_frame = aligned_frames.get_depth_frame()

            if not color_frame or not depth_frame:
                return

            # 데이터 변환
            color_image = np.asanyarray(color_frame.get_data())
            depth_image = np.asanyarray(depth_frame.get_data())

            # ROS 2 메시지로 변환 및 발행
            now = self.get_clock().now().to_msg()
            
            # Color Image
            color_msg = Image()
            color_msg.header.stamp = now
            color_msg.header.frame_id = 'camera_color_optical_frame'
            color_msg.height = color_image.shape[0]
            color_msg.width = color_image.shape[1]
            color_msg.encoding = 'bgr8'
            color_msg.data = color_image.tobytes()
            color_msg.step = color_image.shape[1] * 3
            
            # Depth Image
            depth_msg = Image()
            depth_msg.header.stamp = now
            depth_msg.header.frame_id = 'camera_color_optical_frame'
            depth_msg.height = depth_image.shape[0]
            depth_msg.width = depth_image.shape[1]
            depth_msg.encoding = '16UC1'
            depth_msg.data = depth_image.tobytes()
            depth_msg.step = depth_image.shape[1] * 2

            # Info Header Update
            self.info_msg.header.stamp = now

            self.color_pub.publish(color_msg)
            self.depth_pub.publish(depth_msg)
            self.info_pub.publish(self.info_msg)

        except Exception as e:
            self.get_logger().error(f"Error in timer: {str(e)}")

    def stop(self):
        self.pipeline.stop()

def main(args=None):
    rclpy.init(args=args)
    node = RealsensePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
