import time
from threading import Thread

from logger.logger import Logger
from sensor.light_handler import LightSensor
from sensor.pressure_handler import PressureHandler

finished = False

def sensor_logger(logger: Logger, light_handler: LightSensor, pressure_handler: PressureHandler):
    while not finished:
        light = light_handler.get_light_value()
        pressure = pressure_handler.get_pressure()
        logger.write(f"light: {light}, pressure: {pressure}", no_print = True)

        time.sleep(0.5)

def start(logger: Logger, light_handler: LightSensor, pressure_handler: PressureHandler):
    global finished
    finished = False
    logging_thread = Thread(target = sensor_logger, args = (logger, light_handler, pressure_handler), daemon = True)
    logging_thread.start()

def stop():
    global finished
    finished = True