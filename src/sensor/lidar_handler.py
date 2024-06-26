import asyncio

class LiDARHandler:
    def __init__(self, drone):
        self.drone = drone
        self.altitude: float = -1

    def update_altitude(self, altitude: float) -> None:
        self.altitude = altitude
        return
###################################################以下オープンにする    
    async def invoke_loop(self) -> None:
        async for distance_sensor in self.drone.telemetry.distance_sensor():
            self.update_altitude(distance_sensor.current_distance_m)

    def altitude(self) -> float:
        return self.altitude