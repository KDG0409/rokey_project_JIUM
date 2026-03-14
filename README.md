

🧱 FoundationPose-YOLO Lego Grasping Node (ROS 2)이 패키지는 RGB-D 카메라(RealSense) 영상과 YOLOv8을 이용해 특정 레고 블록을 탐지하고, FoundationPose를 통해 로봇 팔이 잡을 수 있도록 객체의 6D Pose(x, y, z, roll, pitch, yaw)와 상태(Pose Code)를 실시간으로 추정하여 퍼블리시하는 ROS 2 노드입니다.

🌟 주요 기능 (Key Features)Target Detection: YOLOv8을 활용한 지정된 레고 블록(ID) 실시간 탐지6D Pose Estimation: FoundationPose 기반의 빠르고 정밀한 객체 자세 추정Dynamic Camera Intrinsics: /camera/color/camera_info 토픽을 통한 K 매트릭스 자동 로드Coordinate Transformation: TF2를 활용한 카메라 좌표계 $\rightarrow$ 로봇 베이스 좌표계 자동 변환Noise Filtering: Mode(최빈값) 기반 필터링을 통한 안정적인 좌표 퍼블리시 (STABLE_THRESHOLD=20)

🛠 환경 설정 (Prerequisites)
 1. 하드웨어 (Hardware)GPU: NVIDIA RTX 30/40 시리즈 권장 (CUDA 11.x 이상)Camera: Intel RealSense D435iRobot: Doosan Robotics (또는 TF tree base_link $\rightarrow$ link_6를 따르는 6축 다관절 로봇)
 2. 소프트웨어 (Software / Docker)본 프로젝트는 종속성 문제를 방지하기 위해 Docker 환경에서 실행하는 것을 권장합니다.OS: Ubuntu 20.04: Foxy, NVIDIA Container Toolkit(기본 FoundationPose의 기본 docker에서 ROS2 Foxy 추가 설치.)
 3. 의심되는 현상 해결
# 가상환경 활성화 (필요 시)
conda activate my
- openCV, numpy 버전오류: ROS2 Foxy를 추가 설치하면서, 새롭게 install된 openCV와 numpy가 버전 오류를 일으킬 수 있다. -> openCV와 numpy를 지우고, FoundationPose와 맞는 버전 새롭게 설치
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless numpy
# NumPy 설치 (많은 AI 라이브러리의 기반이 되므로 먼저 설치)
pip install numpy==1.23.5
# OpenCV 설치 (headless 버전은 GUI가 없는 서버 환경용이지만, 
# 사용자님의 코드처럼 cv2.imshow를 쓰려면 일반 버전을 설치해야 합니다.)
pip install opencv-python==4.8.0.74
- yolo 업데이트가 필요 -> yolo 업데이트
# ultralytics 패키지 업데이트
pip install --upgrade ultralytics
- realsense2 필요 시 realsense2 install
# pip를 통한 설치
pip install pyrealsense2
 
 
 
 📂 사전 준비
github: https://github.com/NVlabs/FoundationPose

- github에서 zip파일로 다운로드
- https://drive.google.com/drive/folders/1DFezOAD0oD1BblsXVxqDsl8fj0qzB82i
두 개의 weights 모두 다운로드
압축 해제 위치: FoundationPose-main/weights
- mesh 파일 제작 후 .obj형식으로 저장(~/cobot2/FoundationPose-main/demo data를 붙여넣기)
저장 위치: ~/FoundationPose/demo data/lego/mesh

(Weights & Models)노드를 실행하기 전, 다음 가중치 파일들이 weights/ 디렉토리에 위치해야 합니다.PlaintextFoundationPose-main/
└── weights/
    ├── best.pt                   # YOLOv8 레고 탐지 모델
    ├── scorer.pth                # FoundationPose Scorer
    ├── refiner.pth               # FoundationPose Refiner
    └── T_gripper2camera.npy      # 그리퍼-카메라 간 캘리브레이션 행렬
(참고: FoundationPose 공식 가중치는 NVIDIA 드라이브에서 다운로드해야 합니다.)

🚀 실행 방법 (Usage)
 1. Docker 컨테이너 실행
# host terminal
cd ~/FoundationPose-main/docker

# host termainal
bash run_container.sh

DOCKER 이미지 다운로드

- Ubuntu 20.04 버전
- FoundationPose 관련 라이브러리들이 설치됨

### 추가 설치
- ROS2 FOXY 설치
- YOLO 사용 시 YOLO관련 라이브러리 업데이트 필요
- Realsense2 라이브러리 설치 필요(만약, 이미지 토픽으로 사용한다면 필요 없음.)
- RMS_cyclone_dds: ROS2 Humble과 통신 시 필요

- ROS 2 노드 실행Bash# 워크스페이스 소싱
source /opt/ros/foxy/setup.bash

doker 저장 시 run_container.sh를 아래처럼 수정
(예시)
#!/bin/bash
# 1. 기존 컨테이너가 있다면 강제 삭제
docker rm -f foundationpose

# 2. GUI 출력을 위한 권한 허용 (xhost 설정)
xhost +local:docker > /dev/null

# 3. 모든 설정이 적용된 최종 실행 명령
# - foundationpose_success 이미지를 기반으로 실행합니다.
# - 리얼센스 카메라 인식을 위해 --privileged와 -v /dev:/dev를 추가했습니다.
docker run --gpus all \
  --env NVIDIA_DISABLE_REQUIRE=1 \
  -it --net=host \
  --name foundationpose \
  --privileged \
  --cap-add=SYS_PTRACE \
  --security-opt seccomp=unconfined \
  -v /dev:/dev \
  -v ~/FoundationPose-main:/home/donghyun/FoundationPose-main \ #중요!! FoundationPose를 doker에서 연산 할 때, 필수적으로 경로를 허용하여야 함.
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  -v /tmp:/tmp \
  --ipc=host \
  -e DISPLAY=${DISPLAY} \
  -e ROS_DOMAIN_ID=?? \
  -e ROS_LOCALHOST_ONLY=0 \
  -e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \ 
  foundationpose_final_v8 \
  bash -c "
    export PYTHONPATH=/opt/conda/envs/my/lib/python3.8/site-packages:\$PYTHONPATH;
    cd /root/cobot_foxy_ws && bash
  "

# docker container 내부
# 1. 워크스페이스 디렉토리 생성 및 이동
mkdir -p ~/cobot_foxy_ws/src
cd ~/cobot_foxy_ws/src
# 2. ROS 2 패키지 생성 (의존성 포함)
# 의존성: rclpy, std_msgs, sensor_msgs, cv_bridge, tf2_msgs
ros2 pkg create --build-type ament_python cobot_foxy \
--dependencies rclpy std_msgs sensor_msgs cv_bridge tf2_msgs
# cobot2에 있는 FoundationPose.py를 docker내부 ~/cobot_foxy_ws/src/cobot_foxy/cobot_foxy에 저장
# cobot2에 있는 setup.py를 ~/cobot_foxy_ws/src/cobot_foxy의 setup.py의 내용에 ctrl+c, ctrl+v
# 워크스페이스 루트로 이동
cd ~/cobot_foxy_ws
# 심링크 설치 모드로 빌드
colcon build --symlink-install
source install/setup.bash
ros2 run cobot_foxy FoundationPose



📡 ROS 2 인터페이스 (Topics)

📥 Subscribed TopicsTopic NameTypeDescription/camera/color/image_rawsensor_msgs/ImageRealSense RGB 이미지/camera/aligned_depth_to_color/image_rawsensor_msgs/ImageRealSense Depth 이미지 (RGB 정렬)/camera/color/camera_infosensor_msgs/CameraInfo카메라 내부 파라미터 (K 매트릭스)/tftf2_msgs/TFMessage로봇 조인트 및 베이스-카메라 간 좌표 변환/dsr01/detection_startstd_msgs/Int32탐지할 레고 블록의 ID (수신 시 추적 시작)

📤 Published TopicsTopic NameTypeDescription/dsr01/target_lego_posestd_msgs/Float64MultiArray최종 정제된 레고의 [x, y, z, roll, pitch, yaw, pose_code] (단위: mm, deg)

⚙️ 주요 파라미터 (Parameters)
--est_refine_iter (default: 20): 초기 객체 등록(Registration) 시 정밀도. 높을수록 정확하지만 초기 딜레이 발생.
--track_refine_iter (default: 20): 매 프레임 추적(Tracking) 시 정밀도. 프레임 드랍이 심하면 8~10으로 낮출 것.
STABLE_THRESHOLD (코드 내 하드코딩, 기본값: 20): 로봇에게 좌표를 퍼블리시하기 위해 수집하는 안정화 프레임 수.

⌨️ 단축키 (Hotkeys)
q: 프로그램 종료

