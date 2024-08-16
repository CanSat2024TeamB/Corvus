from mavsdk import System

from drone.drone_controller import DroneController
from sensor.lidar_handler import LiDARHandler
from control.battery import Battery_watch
from sensor.gps_handler import GPSHandler
from control.position_manager import PositionManager
from sensor.compass_handler import CompassHandler
from flight.flight_controller import FlightController
from logger.logger import Logger
from sensor.acceleration_velocity import Acceleration_Velocity

class GazeboDroneController(DroneController):
    pixhawk_address: str = "udp://:14540"

    default_log_dir = "/Users/adminair/Documents/Sources/VSCode/Corvus/assets/log"

    def __init__(self, log_dir = default_log_dir):
        self.drone_instance = System()
        self.lidar_handler = LiDARHandler(self.drone_instance)
        self.gps_handler = GPSHandler(self.drone_instance)
        self.battery_watch = Battery_watch(self.drone_instance)
        self.compass_handler = CompassHandler(self.drone_instance)
        self.position_manager = PositionManager(self.drone_instance, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.logger = Logger(log_dir, True)
        self.flight_controller = FlightController(self.drone_instance, self.position_manager, self.logger)
        self.ac_vel = Acceleration_Velocity(self.drone_instance)

        self.tasks = []