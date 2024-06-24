from control import Coordinates,Attitude
import numpy as np

class PositionManager:
    def __init__(self, drone, GPS_handler, Compass_handler, LiDARHandler):
        self.drone = drone
        self.gps_handler = GPS_handler(drone)
        self.compass_handler = Compass_handler(drone)
        self.lidar_handler = LiDARHandler(drone)

    
    def raw_altitude(self) -> float:
        return self.lidar_handler.altitude()
    
    def raw_coordinates(self) -> Coordinates:
        return self.gps_handler.gps_coordinates()
    
    def raw_attitude(self) -> Attitude:
        return self.lidar_handler.attitude()


    def adjusted_altitude(self) -> float:
        lidar = self.lidar_handler.altitude()
        Pitch_deg = self.compass_handler.compass_attitude().get_pitch()
        Roll_deg = self.compass_handler.compass_attitude().get_roll()
        adjusted_altitude = lidar * np.cos(np.deg2rad(Pitch_deg)) * np.cos(np.deg2rad(Roll_deg))
        return adjusted_altitude
    
    def adjusted_coordinates(self) -> Coordinates:
        longitude = self.gps_handler.gps_coordinates().longitude()
        latitude = self.gps_handler.gps_coordinates().latitude()
        return Coordinates(longitude, latitude)