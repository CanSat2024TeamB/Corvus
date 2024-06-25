import asyncio
import mavsdk
from control.coordinates import Coordinates  


class GPSHandler:
    def __init__(self,drone):
        self.drone = drone
        self.coordinates = Coordinates()

    def update_coordinates(self,position) -> None:
        self.coordinates.set_longitude(position.longitude_deg)
        self.coordinates.set_latitude(position.latitude_deg)
        return
#############################################################以下がオープン

    async def invoke_loop(self) -> None:
        async for position in self.drone.telemetry.position():
            self.update_coordinates(position)

    def gps_coordinates(self) -> Coordinates:
        return self.coordinates
    
    async def catch_gps(self)-> None:
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                    break 
                
    async def Get_gps_info(self) -> None:
        async for gps_info in self.telemetry.gps_info():
            self.num_satellites = gps_info.num_satellites
            self.fix_type = gps_info.fix_type

        