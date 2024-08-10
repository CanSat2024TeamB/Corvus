import time
import datetime
from pathlib import Path
from sensor.camera_handler import CameraHandler, ConeDetector

camera_handler = CameraHandler()
cone_detector = ConeDetector(camera_handler)

for i in range(100):
    print(f"capture{i}")
    cone_detector.capture_cone_position_and_save(str(Path(__file__).parent.parent.joinpath(f"assets/log/image_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jpg")), 0.3)
    time.sleep(1)