from pathlib import Path
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
import cv2
import threading
import cone_detector
import time

class CameraHandler:
    def __init__(self):
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration({ "format": "BGR888" })
        self.camera.configure(config)
        self.camera.start()

        camera_config = self.camera.create_preview_configuration()
        self.width = camera_config["main"]["size"][0]
        self.height = camera_config["main"]["size"][1]
    
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
        
    def capture_bgr(self):
        return self.camera.capture_array()

    def capture_rgb(self):
        frame = self.camera.capture_array()
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return image
    
    def capture_and_save(self, path = "image.jpg"):
        image = self.capture_rgb()
        cv2.imwrite(path, image)
    
    def capture_video(self, output_path, length = 10):
        def video_capturer(self, output_path, length):
            video_config = self.camera.create_video_configuration()
            self.camera.configure(video_config)

            encoder = H264Encoder(10000000)

            self.camera.start_recording(encoder, output_path)
            time.sleep(length)
            self.camera.stop_recording()
        
        video_thread = threading.Thread(target = video_capturer, args = (output_path, length,))
        video_thread.start()

class ConeDetector:
    # IMGSZ = 640
    # IOU_THRESHOLD = 0.3
    # CLS_CONE = 4

    # def __init__(self, camera_handler, model_path: str = Path(__file__).parent.parent.joinpath("assets/model/cone_ncnn_model")):
    #     self.camera_handler = camera_handler
    #     self.set_model(str(model_path))

    # def set_model(self, path: str):
    #     self.model_param = str(Path(path).joinpath("model.ncnn.param"))
    #     self.model_bin = str(Path(path).joinpath("model.ncnn.bin"))
    
    # def nms(self, bounding_boxes):
    #     bounding_boxes.sort(key = lambda x: (x[4], x[5]))
    #     result = []

    #     while len(bounding_boxes) > 0:
    #         base = bounding_boxes.pop(-1)
    #         result.append(base)

    #         base_size = (base[2] - base[0]) * (base[3] - base[1])
    #         i = len(bounding_boxes) - 1

    #         while i >= 0:
    #             target = bounding_boxes[i]
    #             if target[4] != base[4]:
    #                 break

    #             target_size = (target[2] - target[0]) * (target[3] - target[1])
    #             overlap_size = max(0, min(base[2], target[2]) - max(base[0], target[0])) * max(0, min(base[3], target[3]) - max(base[1], target[1]))
    #             iou = overlap_size / (base_size + target_size - overlap_size)
    #             if iou > ConeDetector.IOU_THRESHOLD:
    #                 del bounding_boxes[i]
    #             i -= 1
                
    #     return result

    # def predict(self, image, conf = 0.1):
    #     net = ncnn.Net()
    #     net.load_param(self.model_param)
    #     net.load_model(self.model_bin)

    #     extractor = net.create_extractor()

    #     image_height = image.shape[0]
    #     image_width = image.shape[1]

    #     mat_in = ncnn.Mat.from_pixels_resize(image, ncnn.Mat.PixelType.PIXEL_BGR2RGB, image_width, image_height, ConeDetector.IMGSZ, ConeDetector.IMGSZ)
    #     mat_in.substract_mean_normalize([], [1 / 255, 1 / 255, 1 / 255])

    #     extractor.input("in0", mat_in)
    #     ret, mat_out = extractor.extract("out0")
    #     out = np.array(mat_out)

    #     output_list = out.T
    #     result = []
    #     for output_data in output_list:
    #         x1 = int((output_data[0] - output_data[2] / 2) * image_width / ConeDetector.IMGSZ)
    #         y1 = int((output_data[1] - output_data[3] / 2) * image_height / ConeDetector.IMGSZ)
    #         x2 = int((output_data[0] + output_data[2] / 2) * image_width / ConeDetector.IMGSZ)
    #         y2  =int((output_data[1] + output_data[3] / 2) * image_height / ConeDetector.IMGSZ)

    #         cls = np.argmax(output_data[4:])
    #         if output_data[4 + cls] > conf:
    #             result.append([x1, y1, x2, y2, cls, output_data[4 + cls]])

    #     return self.nms(result)
    
    # def get_cone_bouding_box(self, image, conf = 0.5) -> list[int, int, int, int]:
    #     cone_box = None
    #     max_conf = 0

    #     result_list = self.predict(image, conf)
    #     for result in result_list:
    #         box = result[:4]
    #         cls = result[4]
    #         conf = result[5]
            
    #         if cls != ConeDetector.CLS_CONE or conf < max_conf:
    #             continue

    #         cone_box = box
    #         max_conf = conf
        
    #     return cone_box
    
    # def get_cone_position(self, image, conf = 0.5):
    #     cone_box = self.get_cone_bouding_box(image, conf)
    #     if cone_box is None:
    #         return [None, None]
    #     else:
    #         normalized_x = float(cone_box[0] + cone_box[2]) / self.camera_handler.get_width() - 1
    #         normalized_y = float(cone_box[1] + cone_box[3]) / self.camera_handler.get_height() - 1
    #         return [normalized_x, normalized_y]
        
    # def capture_cone_position(self, conf = 0.1):
    #     image = self.camera_handler.capture()

    #     if not image is None:
    #         #det_start = time.perf_counter()
    #         result = self.get_cone_position(image, conf)
    #         #det_end = time.perf_counter()
    #         #print(f"detection: {(det_end - det_start) * 1000} ms")
    #         return result
    #     else:
    #         return [None, None]

    IOU_THRESHOLD = 0.1
    condition = threading.Condition()

    def __init__(self, camera_handler, model_path: str = Path(__file__).parent.parent.joinpath("assets/model/cone_ncnn_model_v9_320"), imgsz = 320):
        self.camera_handler = camera_handler
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
        while not self.finished:
            frame = self.camera_handler.capture_bgr()
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
            time.sleep(2)

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
            #det_start = time.perf_counter()
            result = cone_detector.get_pos(image, conf)
            #det_end = time.perf_counter()
            #print(f"detection: {(det_end - det_start) * 1000} ms")
            return result
        else:
            return [None, None]
            
# 使い方
# camera_handler = CameraHandler()
# cone_detector = ConeDetector(camera_handler, Path(__file__).parent.parent.parent.joinpath("assets/model/cone.pt"))
# while True:
#     os = cone_detector.capture_cone_position()
#     print(pos)

def test1():
    camera_handler = CameraHandler()
    cone_detector = ConeDetector(camera_handler, Path(__file__).parent.parent.parent.joinpath("assets/model/cone_ncnn_model_v9_320"), 320)
    cone_detector.start()
    start = time.perf_counter()
    with open("hello.txt", 'w') as f:
        while True:
            time.sleep(0.1)
            pos = cone_detector.get_pos()
            now = time.perf_counter()
            f.write(f"{now - start}s {pos}\n")
            if now - start > 15:
                break
    cone_detector.stop()


def test2():
    camera_handler = CameraHandler()
    image = camera_handler.capture_rgb()
    cv2.imwrite("capture.png", image)

test1()