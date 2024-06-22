import asyncio
import mavsdk

class GPSHandler:
    def __init__(self,drone,Coordinates):
        self.drone = drone
        self.coordinates = Coordinates()

    async def get_coordinates(self) -> None:
        async for position in self.drone.telemetry.position():
            self.coordinates.set_x(position.latitude_deg)
            self.coordinates.set_y(position.longitude_deg)
    
    async def invoke_loop(self) -> None:
        while True:
            await self.get_coordinates()
            await asyncio.sleep(0.01)s