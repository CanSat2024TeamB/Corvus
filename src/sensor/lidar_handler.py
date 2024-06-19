class LiDARHandler:
    def __init__(self, drone):
        self.drone = drone
        self.altitude: float = 0
    
    def altitude(self) -> float:
        return altitude
    
    def update_altitude(self, altitude: float) -> None:
        self.altitude = altitude
        return
    
    async def invoke(self):
        async for distance_sensor in drone.telemetry.distance_sensor():
            update_altitude(distance_sensor.current_distance_m)