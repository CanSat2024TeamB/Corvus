from pathlib import Path
from ultralytics import YOLO
from picamera2 import Picamera2
import cv2

class CameraHandler:
    def __init__(self, model_path: str = Path(__file__).parent.parent.joinpath("assets/model/cone.pt")):
        self.camera = Picamera2()
        self.camera.start()

        camera_config = self.camera.create_preview_configuration()
        self.width = camera_config["main"]["size"][0]
        self.height = camera_config["main"]["size"][1]

        self.set_model(model_path)
    
    def get_width(self):
        return self.width
    
    def get_height(self):
        return self.height
    
    def set_model(self, path: str):
        self.model = YOLO(path)
        
    def capture(self):
        frame = self.camera.capture_array()
        image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return image
    
    def capture_and_save(self, path = "image.jpg"):
        image = self.capture()
        cv2.imwrite(path, image)

class ConeDetector:
    def __init__(self, camera_handler):
        self.camera_handler = camera_handler
    
    def get_cone_bouding_box(self, image, conf = 0.5) -> list[int, int, int, int]:
        cone_box = None
        max_conf = 0

        result = self.model.predict(image, conf = conf, verbose = False)
        boxes = result[0].boxes
        for i in range(len(boxes.cls)):
            cls = boxes.cls[i]
            conf = boxes.conf[i]
            name = result[0].names[int(cls)]

            if name != "cone" or conf < max_conf:
                continue

            box = boxes.xyxy[i]
            cone_box = [int(box[0]), int(box[1]), int(box[2]), int(box[3])]
            max_conf = conf

        return cone_box
    
    def get_cone_position(self, image, conf = 0.5):
        cone_box = self.get_cone_bouding_box(image, conf)
        if cone_box is None:
            return [None, None]
        else:
            normalized_x = float(cone_box[0] + cone_box[2]) / self.camera_handler.get_width() - 1
            normalized_y = float(cone_box[1] + cone_box[3]) / self.camera_handler.get_height() - 1
            return [normalized_x, normalized_y]
        
    def capture_cone_position(self, conf = 0.1):
        image = self.camera_handler.capture()
        if not image is None:
            return self.get_cone_position(image, conf)
        else:
            return [None, None]
            
# 使い方
# camera_handler = CameraHandler(model_path=Path(__file__).parent.parent.parent.joinpath("assets/model/cone.pt"))
# cone_detector = ConeDetector(camera_handler)
# while True:
#     os = cone_detector.capture_cone_position()
#     print(pos)

def test1():
    camera_handler = CameraHandler(model_path=Path(__file__).parent.parent.parent.joinpath("assets/model/cone.pt"))
    cone_detector = ConeDetector(camera_handler)
    image = camera_handler.capture()
    box = cone_detector.get_cone_bouding_box(image, 0.5)
    if not box is None:
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[4]), (255, 0, 0))
    cv2.imwrite("~/detect.png", image)

def test2():
    camera_handler = CameraHandler(model_path=Path(__file__).parent.parent.parent.joinpath("assets/model/cone.pt"))
    cone_detector = ConeDetector(camera_handler)
    while True:
        pos = cone_detector.capture_cone_position()
        print(pos)