class PositionManager:
    def __init__(self, drone, gps_handler, compass_handler, lidar_handler):
        self.drone = drone
        self.gps_handler = gps_handler
        self.compass_handler = compass_handler
        self.lidar_handler = lidar_handler
    
    def adjusted_altitude() -> float:
        return self.lidar_handler.altitude()