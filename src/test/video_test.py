import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import time
from sensor.camera_handler import CameraHandler

camera_handler = CameraHandler()

print("start capturing")
camera_handler.capture_video("test.mp4", 10)
print("finish")