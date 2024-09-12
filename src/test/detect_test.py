import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.joinpath("assets/module")))

from pathlib import Path
import cv2
import numpy as np
import os
import threading
import cone_detector
import time

def detect(image, conf, output_path):
    if image is None:
        return
    pos = cone_detector.get_pos(image, conf)
    height = image.shape[0]
    width = image.shape[1]
    if pos[0] >= -1:
        x = int((pos[0] + 1) / 2 * width)
        y = int((pos[1] + 1) / 2 * height)
        result = cv2.circle(image, (x, y), 25, (0, 0, 255), thickness = 5)
        cv2.imwrite(output_path, result)

cone_detector.load_model(str(Path(__file__).parent.parent.parent.joinpath("assets/model/cone_ncnn_model_v9_320_opt")), 320)
in_path = "/home/admin/imgs/"
out_path = "/home/admin/result/"
imgs = os.listdir(in_path)
for img in imgs:
    img_path = in_path + img
    image = cv2.imread(img_path)
    detect(image, 0.3, out_path + img)