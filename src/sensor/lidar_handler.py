import asyncio

class LiDARHandler:
    def __init__(self, drone):
        self.drone = drone
        self.altitude: float = None
        asyncio.run(self.invoke_loop())
    
    def update_altitude(self, altitude: float) -> None:
        self.altitude = altitude
        return
    
    async def invoke_loop(self) -> None:
        async for distance_sensor in self.drone.telemetry.distance_sensor():
            self.update_altitude(distance_sensor.current_distance_m)

###################################################以下オープンにする

    def altitude(self) -> float:
        return self.altitude