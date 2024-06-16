import os
for p in os.environ['PATH'].split(os.pathsep):
    if os.path.isdir(p):
        os.add_dll_directory(p)

import corvus_image
import numpy
import matplotlib.pyplot as plt

camera = corvus_image.camera_handler()
cascade = corvus_image.cascade_handler("assets/haarcascade_frontalface_alt.xml")
#img_raw = corvus_image.image("assets/face_sample2.jpg")
img_raw = camera.capture()
time = cascade.mesure_prediction_time(img_raw)
print("time:", time, "ms")