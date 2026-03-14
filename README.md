#  JIUM (지음) : AI 기반 협동 로봇 작업 어시스턴트
> K-Digital Training 과정 협동-2팀(곽준영, 김동국, 박경모, 이동현) 프로젝트

##  FoundationPose-YOLO Lego Grasping Node (ROS 2) & Voice Command
이 패키지는 RGB-D 카메라(RealSense) 영상과 YOLOv8을 이용해 특정 레고 블록을 탐지하고, FoundationPose를 통해 로봇 팔이 잡을 수 있도록 객체의 6D Pose(x, y, z, roll, pitch, yaw)와 상태(Pose Code)를 실시간으로 추정하여 퍼블리시하는 ROS 2 노드입니다.

여기에 **음성 인식(Whisper) 및 LLM(GPT-4o)** 기반의 자연어 명령 처리와 두산 협동 로봇 제어 기능이 추가되어 종합적인 스마트 작업 어시스턴트 시스템으로 확장되었습니다.

---

##  주요 기능 (Key Features)

### 1. 객체 인식 및 6D Pose 추정 (Vision AI)
* **Target Detection**: YOLOv8을 활용한 지정된 레고 블록(ID) 실시간 탐지
* **6D Pose Estimation**: FoundationPose 기반의 빠르고 정밀한 객체 자세 추정
* **Dynamic Camera Intrinsics**: `/camera/color/camera_info` 토픽을 통한 K 매트릭스 자동 로드
* **Coordinate Transformation**: TF2를 활용한 카메라 좌표계 $\rightarrow$ 로봇 베이스 좌표계 자동 변환
* **Noise Filtering**: Mode(최빈값) 기반 필터링을 통한 안정적인 좌표 퍼블리시 (STABLE_THRESHOLD=20)

### 2. 음성 명령 및 통합 제어 (NLP & Control)
* **Voice & LLM Command**: OpenAI Whisper API를 통해 음성을 텍스트화(STT)하고, GPT-4o를 활용해 문장에서 대상 객체와 목적지 키워드를 추출합니다.
* **Human-Robot Interaction**: MediaPipe로 작업자의 손(Hand Landmark) 위치를 실시간 추적하여 안전한 물품 전달을 돕습니다.
* **Robot Pick & Place**: 추출된 6D Pose를 바탕으로 두산 협동 로봇(m0609)과 OnRobot RG2 그리퍼를 제어하여 임무를 수행합니다.

---

1. **명령 입력**: 작업자가 마이크로 지시사항을 말합니다.
2. **AI 분석**: STT가 텍스트로 변환하고, LLM이 키워드(객체, 목적지)를 추출하여 전달합니다.
3. **비전 탐색**: YOLO와 FoundationPose가 객체의 6D 위치/자세를 계산하여 로봇 좌표계로 변환합니다.
4. **로봇 구동**: 로봇이 해당 좌표로 이동하여 대상 객체를 파지 후 목표 위치로 이동시킵니다.

---

##  주요 파일 구조 (Repository Structure)

| 파일명 | 설명 |
|---|---|
| `run_system.launch.py` | 메인 로봇 제어, 음성 인식, 비전 디텍션 노드를 한 번에 실행하는 통합 런치 파일 |
| `stage_place.py` | 로봇 움직임 제어 및 전체 Task Queue를 관리하는 메인 워커 노드 |
| `get_keyword.py` / `stt.py` | Whisper STT 변환 및 GPT-4o 기반 키워드 추출 서비스 노드 |
| `detection.py` / `yolo.py` | YOLOv8 객체 탐지 및 MediaPipe 손 랜드마크 추적 노드 |
| `FoundationPose.py` | 객체의 6D Pose 및 상태를 실시간으로 추정하는 핵심 비전 노드 |
| `realsense_publisher.py` | RealSense 카메라 영상 및 Depth 데이터를 ROS2 토픽으로 발행 |
| `onrobot.py` | Modbus TCP 통신을 이용한 OnRobot RG2 그리퍼 제어 모듈 |

---

##  환경 설정 (Prerequisites)

### 1. 하드웨어 (Hardware)
* **GPU**: NVIDIA RTX 30/40 시리즈 권장 (CUDA 11.x 이상)
* **Camera**: Intel RealSense D435i
* **Robot**: Doosan Robotics (또는 TF tree `base_link` $\rightarrow$ `link_6`를 따르는 6축 다관절 로봇) / OnRobot RG2 그리퍼

### 2. 소프트웨어 (Software / Docker)
본 프로젝트는 종속성 문제를 방지하기 위해 Docker 환경에서 실행하는 것을 권장합니다.
* **OS**: Ubuntu 20.04: Foxy, NVIDIA Container Toolkit
*(기본 FoundationPose의 기본 docker에서 ROS2 Foxy 추가 설치.)*

---

##  의심되는 현상 해결 (Troubleshooting)

**1. 가상환경 활성화 (필요 시)**
```bash
conda activate my
```

**2. openCV, numpy 버전오류**
ROS2 Foxy를 추가 설치하면서, 새롭게 install된 openCV와 numpy가 버전 오류를 일으킬 수 있습니다.
-> openCV와 numpy를 지우고, FoundationPose와 맞는 버전 새롭게 설치
```bash
pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless numpy
```
* **NumPy 설치** (많은 AI 라이브러리의 기반이 되므로 먼저 설치):
  ```bash
  pip install numpy==1.23.5
  ```
* **OpenCV 설치** (headless 버전은 GUI가 없는 서버 환경용이지만, `cv2.imshow`를 쓰려면 일반 버전을 설치해야 합니다.):
  ```bash
  pip install opencv-python==4.8.0.74
  ```

**3. YOLO 업데이트가 필요할 경우**
```bash
pip install --upgrade ultralytics
```

**4. realsense2 설치 (필요 시)**
만약 이미지 토픽으로 사용한다면 필요 없습니다.
```bash
pip install pyrealsense2
```

---

##  사전 준비 (Weights & Models)

1. **GitHub**: [https://github.com/NVlabs/FoundationPose](https://github.com/NVlabs/FoundationPose) 에서 zip 파일 다운로드
2. **Weights 다운로드**: [Google Drive 링크](https://drive.google.com/drive/folders/1DFezOAD0oD1BblsXVxqDsl8fj0qzB82i)에서 두 개의 weights 모두 다운로드 후 압축 해제 
   * **위치**: `FoundationPose-main/weights`
3. **Mesh 파일**: `mesh` 파일 제작 후 `.obj` 형식으로 저장 ( `~/cobot2/FoundationPose-main/demo data` 를 붙여넣기)
   * **위치**: `~/FoundationPose/demo data/lego/mesh`

노드를 실행하기 전, 다음 가중치 파일들이 `weights/` 디렉토리에 위치해야 합니다.
```plaintext
FoundationPose-main/
└── weights/
    ├── best.pt              # YOLOv8 레고 탐지 모델
    ├── scorer.pth           # FoundationPose Scorer
    ├── refiner.pth          # FoundationPose Refiner
    └── T_gripper2camera.npy # 그리퍼-카메라 간 캘리브레이션 행렬
```
*(참고: FoundationPose 공식 가중치는 NVIDIA 드라이브에서 다운로드해야 합니다.)*

---

##  실행 방법 (Usage)

### 1. Docker 컨테이너 실행 (Host Terminal)

```bash
cd ~/FoundationPose-main/docker
bash run_container.sh
```

**[참고] DOCKER 이미지 환경**
* Ubuntu 20.04 버전
* FoundationPose 관련 라이브러리들이 설치됨
* **추가 설치 목록**:
  * ROS2 FOXY 설치
  * YOLO 사용 시 YOLO 관련 라이브러리 업데이트 필요
  * Realsense2 라이브러리 설치 필요 (이미지 토픽 사용 시 불필요)
  * RMS_cyclone_dds: ROS2 Humble과 통신 시 필요

**[참고] Docker 저장 시 `run_container.sh` 수정 예시**
```bash
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
-v ~/FoundationPose-main:/home/donghyun/FoundationPose-main \ # 중요!! 연산 시 필수 경로 허용
-v /tmp/.X11-unix:/tmp/.X11-unix \
-v /tmp:/tmp \
--ipc=host \
-e DISPLAY=${DISPLAY} \
-e ROS_DOMAIN_ID=?? \
-e ROS_LOCALHOST_ONLY=0 \
-e RMW_IMPLEMENTATION=rmw_cyclonedds_cpp \
foundationpose_final_v8 \
bash -c "export PYTHONPATH=/opt/conda/envs/my/lib/python3.8/site-packages:$PYTHONPATH; cd /root/cobot_foxy_ws && bash"
```

### 2. 작업 공간 빌드 및 환경 설정 (Docker 컨테이너 내부)

```bash
# 워크스페이스 소싱
source /opt/ros/foxy/setup.bash

# 1. 워크스페이스 디렉토리 생성 및 이동
mkdir -p ~/cobot_foxy_ws/src
cd ~/cobot_foxy_ws/src

# 2. ROS 2 패키지 생성 (의존성 포함)
ros2 pkg create --build-type ament_python cobot_foxy \
--dependencies rclpy std_msgs sensor_msgs cv_bridge tf2_msgs

# * cobot2에 있는 FoundationPose.py를 ~/cobot_foxy_ws/src/cobot_foxy/cobot_foxy에 저장
# * cobot2에 있는 setup.py를 ~/cobot_foxy_ws/src/cobot_foxy/setup.py 내용에 붙여넣기

# 3. 워크스페이스 루트로 이동 및 빌드
cd ~/cobot_foxy_ws
colcon build --symlink-install
source install/setup.bash
```

### 3. 시스템 노드 실행
각각 별도의 터미널(Docker 내부)을 열어 아래 명령어들을 실행합니다.

**터미널 1 (카메라 퍼블리셔 및 FoundationPose):**
```bash
ros2 run cobot_foxy realsense_publisher
ros2 run cobot_foxy FoundationPose
```

**터미널 2 (통합 제어 - 로봇, 음성, 디텍션):**
```bash
ros2 launch cobot_foxy run_system.launch.py
```

---

##  ROS 2 인터페이스 (Topics)

###  Subscribed Topics
| Topic Name | Type | Description |
|---|---|---|
| `/camera/color/image_raw` | `sensor_msgs/Image` | RealSense RGB 이미지 |
| `/camera/aligned_depth_to_color/image_raw` | `sensor_msgs/Image` | RealSense Depth 이미지 (RGB 정렬) |
| `/camera/color/camera_info` | `sensor_msgs/CameraInfo` | 카메라 내부 파라미터 (K 매트릭스) |
| `/tf` | `tf2_msgs/TFMessage` | 로봇 조인트 및 베이스-카메라 간 좌표 변환 |
| `/dsr01/detection_start` | `std_msgs/Int32` | 탐지할 레고 블록의 ID (수신 시 추적 시작) |

###  Published Topics
| Topic Name | Type | Description |
|---|---|---|
| `/dsr01/target_lego_pose` | `std_msgs/Float64MultiArray` | 최종 정제된 레고의 `[x, y, z, roll, pitch, yaw, pose_code]` (단위: mm, deg) |

---

##  주요 파라미터 (Parameters)
* `--est_refine_iter` (default: 20): 초기 객체 등록(Registration) 시 정밀도. 높을수록 정확하지만 초기 딜레이 발생.
* `--track_refine_iter` (default: 20): 매 프레임 추적(Tracking) 시 정밀도. 프레임 드랍이 심하면 8~10으로 낮출 것.
* `STABLE_THRESHOLD` (코드 내 하드코딩, 기본값: 20): 로봇에게 좌표를 퍼블리시하기 위해 수집하는 안정화 프레임 수.

---

##  단축키 (Hotkeys)
* `q` : 프로그램 종료
