import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import time
from sensor.camera_handler import CameraHandler

camera_handler = CameraHandler.get_instance()

print("start capturing")
camera_handler.capture_video("test.mp4", 10)
time.sleep(15)
print("finish")