import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import time
import datetime
from pathlib import Path
from sensor.camera_handler import CameraHandler, ConeDetector

camera_handler = CameraHandler.get_instance()

# try:
#     if not camera_handler.is_connected():
#         raise RuntimeError("Camera is not connected. Stopped the precies land sequence.")
#     print("ok")
# except RuntimeError as e:
#     print(e)
# else:
#     cone_detector = ConeDetector(camera_handler)
#     print(cone_detector.get_pos())

# print("finish")

cone_detector = ConeDetector(camera_handler)

try:
    try:
        while True:
            cone_detector.start()
            pos = cone_detector.get_pos()
            print(f"pos: {pos}")
    except RuntimeError as e:
        print("<inner> error has occured!")
except:
    print("<outer> error has occured!")