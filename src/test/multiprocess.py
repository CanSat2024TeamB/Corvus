import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import time
from multiprocessing import Process, Array, Value
from pathlib import Path

from sensor.camera_handler import CameraHandler, ConeDetector

def counter(num):
        for i in range(8000):
            print(i)
            num.value = i
            #time.sleep(0.05)

def multiprocess():
    # arr = Array("f", 2)
    num = Value("i", 0)
    process = Process(target=counter, args=(num,), daemon=True)
    process.start()
    for i in range(10):
        print("arr read:", num.value)
        time.sleep(0.1)
    process.join()

def capturer(cone_detector: ConeDetector, arr: Array):
    while True:
        pos = cone_detector.capture_cone_position(0.3, True)
        arr[0] = pos[0]
        arr[1] = pos[1]

def camera():
    camera_handler = CameraHandler.get_instance()
    cone_detector = ConeDetector(camera_handler)
    pos = Array("f", 2)

    process = Process(target=capturer, args=(cone_detector, pos,), daemon=True)
    process.start()

    i = 0
    while True:
        print(i, pos)
        i += 1
        time.sleep(0.05)

def camera2():
    camera_handler = CameraHandler.get_instance()
    cone_detector = ConeDetector(camera_handler)
    cone_detector.start(0.3)
    
    while True:
        pos = cone_detector.get_pos()
        print(pos)
        time.sleep(0.1)

if __name__ == "__main__":
    multiprocess()