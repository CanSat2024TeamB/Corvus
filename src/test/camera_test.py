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


# cone_detector = ConeDetector(camera_handler)
# cone_detector.start(0.3)

# with open("camera_test.txt", "w") as f:
#     while True:
#         pos = cone_detector.get_pos()
#         f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %f')} {pos}\n")
#         print("hi")
#         time.sleep(0.1)

def test_detection(): ##画像認識だけ？
    cone_detector = ConeDetector(camera_handler)

    for i in range(20):
        print(i)
        cone_detector.capture_cone_position_and_save(f"/home/admin/corvus/assets/log/img_{i}.png", 0.5)
        time.sleep(1)

def test_color_detection(): ###色認識だけ？
    cone_detector = ConeDetector(camera_handler)
    count = 0
    pos = [None, None]
    while count < 10 and pos[0] is None:
        count += 1
        image = camera_handler.capture_bgr()
        pos = cone_detector.calc_color_center(image)
        cone_detector.draw_circle_and_save(
            image, 
            pos[0], 
            pos[1], 
            f"/home/admin/corvus/assets/log/color_detect_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.png"
        )
        time.sleep(1)

def test_detection_using_color():
    cone_detector = ConeDetector(camera_handler)
    cone_detector.start(0.3)

    loop_start = time.perf_counter()
    while True:
        start = time.perf_counter()
        pos = cone_detector.get_pos(use_color_assist = True)
        end = time.perf_counter()

        print(pos)
        print(f"time: {(end - start) * 1000} ms")
        
        time.sleep(0.5)
        now = time.perf_counter()
        if (now - loop_start > 10):
            break
    
    cone_detector.stop()

if __name__ == "__main__":
    test_color_detection()