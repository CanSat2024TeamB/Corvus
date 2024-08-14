import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.joinpath("assets/module")))

from pathlib import Path
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import cv2
import numpy as np
import threading
import cone_detector
import time

class CameraHandler:
    _unique_instance = None

    def __new__(self):
        raise NotImplementedError("Cannot generate instance by constructor. Call get_instance() method instead.")
    
    @classmethod
    def __internal_new__(self):
        self._is_connected = False

        try:
            self.camera = Picamera2()
            config = self.camera.create_preview_configuration({ "format": "BGR888" })
            self.camera.configure(config)
            self.camera.start()
        except Exception as e:
            print(f"Cannot connect the camera.")
        else:
            self._is_connected = True
            camera_config = self.camera.create_preview_configuration()
            self.width = camera_config["main"]["size"][0]
            self.height = camera_config["main"]["size"][1]
        finally:
            return super().__new__(self)

    @classmethod
    def get_instance(self):
        if self._unique_instance is None:
            self._unique_instance = self.__internal_new__()
        return self._unique_instance
    
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height

    def is_connected(self):
        return self._is_connected
        
    def capture_bgr(self):
        image = self.camera.capture_array()
        return cv2.rotate(image, cv2.ROTATE_180) # カメラの取り付け上下が逆になってることを考慮

    def capture_rgb(self):
        frame = self.camera.capture_array()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return cv2.rotate(image, cv2.ROTATE_180) # カメラの取り付け上下が逆になってることを考慮
    
    def capture_and_save(self, path = "image.jpg"):
        image = self.capture_rgb()
        cv2.imwrite(path, image)
    
    def capture_video(self, output_path, length = 10):
        def video_capturer(self, output_path, length):
            video_config = self.camera.create_video_configuration()
            self.camera.stop()
            self.camera.configure(video_config)

            encoder = H264Encoder(10000000)
            output = FfmpegOutput(output_path)

            try:
                self.camera.start_recording(encoder, output)
                time.sleep(length)
                self.camera.stop_recording()
                self.camera.start()
            except Exception as e:
                print("Error has occured. Stopped capturing video")
                print(e)
        
        video_thread = threading.Thread(target = video_capturer, args = (self, output_path, length,))
        video_thread.start()

class ConeDetector:
    IOU_THRESHOLD = 0.1
    condition = threading.Condition()

    def __init__(self, camera_handler, model_path: str = Path(__file__).parent.parent.parent.joinpath("assets/model/cone_ncnn_model_v9_320_opt"), imgsz = 320):
        self.camera_handler: CameraHandler = camera_handler
        cone_detector.load_model(str(model_path), imgsz)

        self.frame = None
        self.pos = [None, None]
        self.finished = False
    
    def get_pos(self):
        self.condition.acquire()
        pos = self.pos
        self.condition.release()
        return pos
    
    def reader(self):
        try:
            while not self.finished:
                frame = self.camera_handler.capture_bgr()
                self.condition.acquire()
                self.frame = frame
                self.condition.notify()
                self.condition.release()
        except Exception as e:
            print("Could not normally capture image.")
            frame = np.zeros((self.camera_handler.get_height, self.camera_handler.get_width, 3))
            self.condition.acquire()
            self.frame = frame
            self.condition.notify()
            self.condition.release()
    
    def detector(self, conf = IOU_THRESHOLD):
        while not self.finished:
            self.condition.acquire()
            if self.frame is None:
                self.condition.wait()
            frame = self.frame
            self.condition.release()

            pos = cone_detector.get_pos(frame, conf)
            
            self.condition.acquire()
            if pos[0] < -1:
                self.pos = [None, None]
            else:
                self.pos = pos
            self.condition.release()

    def start(self, conf = IOU_THRESHOLD):
        reader_thread = threading.Thread(target = self.reader, daemon = True)
        detector_thread = threading.Thread(target = self.detector, args = (conf,), daemon = True)

        reader_thread.start()
        detector_thread.start()
    
    def stop(self):
        self.finished = True

    def capture_cone_position(self, conf = IOU_THRESHOLD):
        image = self.camera_handler.capture_bgr()

        if not image is None:
            result = cone_detector.get_pos(image, conf)
            if result[0] >= -1:
                return [result[0], result[1]]
            else:
                return [None, None]
        else:
            return [None, None]

    def capture_cone_position_and_save(self, output_path, conf = IOU_THRESHOLD):
        image = self.camera_handler.capture_bgr()

        if not image is None:
            result = cone_detector.get_pos(image, conf)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if result[0] >= -1:
                image = cv2.circle(image, (int((result[0] + 1) / 2 * 640), int((-result[1] + 1) / 2 * 480)), 25, (255, 255, 255), thickness = 5)
                cv2.imwrite(output_path, image)
                return result
            else:
                cv2.imwrite(output_path, image)
                return [None, None]
        else:
            return [None, None]

# def test1():
#     camera_handler = CameraHandler()
#     cone_detector = ConeDetector(camera_handler, Path(__file__).parent.parent.parent.joinpath("assets/model/cone_ncnn_model_v9_320"), 320)
#     cone_detector.start()
#     start = time.perf_counter()
#     while True:
#         time.sleep(0.1)
#         pos = cone_detector.get_pos()
#         now = time.perf_counter()
#         print(f"{now - start}s {pos}\n")
#         if now - start > 15:
#             break
#     cone_detector.stop()

# def test2():
#     camera_handler = CameraHandler()
#     image = camera_handler.capture_rgb()
#     cv2.imwrite("capture.png", image)

# def test3():
#     camera_handler = CameraHandler()
#     camera_handler.capture_video("test.mp4")

#test3()