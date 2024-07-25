from ultralytics import YOLO
import cv2
from pathlib import Path

class CameraHandler:
    def __init__(self, device_id: int = 0, model_path: str = Path(__file__).parent.parent.joinpath("assets/model/cone.pt")):
        self.camera = cv2.VideoCapture(device_id)
        self.width = None
        self.height = None
        if self.camera.isOpened():
            self.width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            self.height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.set_model(model_path)
    
    def set_model(self, path: str):
        self.model = YOLO(path)
        
    def capture(self):
        ret, frame = self.camera.read()
        if ret:
            return frame
        else:
            return None
    
    def get_cone_bouding_box(self, image, conf = 0.1) -> list[list[int, int, int, int]]:
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
    
    def get_cone_position(self, image, conf = 0.1):
        cone_box = self.get_cone_bouding_box(image, conf)
        if cone_box is None or (self.width is None or self.height is None):
            return [None, None]
        else:
            normalized_x = float(cone_box[0] + cone_box[2]) / self.width - 1
            normalized_y = float(cone_box[1] + cone_box[3]) / self.width - 1
            return [normalized_x, normalized_y]
    
    def capture_cone_position(self, conf = 0.1):
        image = self.capture()
        if not image is None:
            # cone_box = self.get_cone_bouding_box(image, conf = 0.1)
            # if not cone_box is None:
            #     cv2.rectangle(image, (cone_box[0], cone_box[1]), (cone_box[2], cone_box[3]), (255, 0, 0))
            # cv2.imshow("h", image)
            return self.get_cone_position(image, conf)
        else:
            return [None, None]
            
# 使い方
# camera_handler = CameraHandler(model_path=Path(__file__).parent.parent.parent.joinpath("assets/model/cone.pt"))
# while True:
#     pos = camera_handler.capture_cone_position(0.5)
#     print(pos)