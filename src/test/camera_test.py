import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import time
import datetime
from pathlib import Path
from sensor.camera_handler import CameraHandler, ConeDetector

import cv2

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

def test_camera():
    image_bgr = camera_handler.capture_bgr()
    image_rgb = camera_handler.capture_rgb()
    cv2.imwrite("bgr.png", image_bgr)
    cv2.imwrite("rgb.png", image_rgb)

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
    while count < 10:
        count += 1
        image = camera_handler.capture_bgr()
        pos = cone_detector.calc_color_center(image)
        print(count)
        print(pos)
        cone_detector.draw_circle_and_save(image, pos[0], pos[1], f"/home/admin/corvus/assets/log/color_detect_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.png")
        time.sleep(1)

def test_detection_using_color():
    cone_detector = ConeDetector(camera_handler)
    cone_detector.start(0.3, True)

    pos_prev = [None, None]
    start = time.perf_counter()

    while True:
        pos = cone_detector.get_pos()
        if pos_prev[0] is None:
            if pos[0] is None:
                continue
        elif pos_prev[0] is not None:
            if pos[0] is not None and pos[0] == pos_prev[0]:
                continue
        now = time.perf_counter()
        print(f"{(now - start) * 1000} ms")
        print(pos)
        start = time.perf_counter()
        pos_prev = pos

def test_detection_using_color2():
    cone_detector = ConeDetector(camera_handler)
    i = 0
    while True:
        start = time.perf_counter()
        pos = cone_detector.capture_cone_position(0.3, True)
        end = time.perf_counter()

        print(f"{i}: {(end - start) * 1000} ms")
        print(pos)
        i += 1

        time.sleep(1)

if __name__ == "__main__":
    test_detection_using_color2()