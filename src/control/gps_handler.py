import asyncio
import mavsdk

import multiprocessing

from control.coordinates import Coordinates  


class GPSHandler:
    def __init__(self, drone):
        self.drone = drone
        self.latitude_deg = multiprocessing.Value("f", 0.0)
        self.longitude_deg = multiprocessing.Value("f", 0.0)
        self.absolute_altitude_m = multiprocessing.Value("f", 0.0)

    async def update_coordinates(self, latitude_deg, longitude_deg, absolute_altitude_m) -> None:
        """最新のGPSデータで座標を更新"""
        self.latitude_deg.value = latitude_deg
        self.longitude_deg.value = longitude_deg
        self.absolute_altitude_m.value = absolute_altitude_m
        return

    async def invoke_loop(self) -> None:
        position_stream = self.drone.telemetry.position()

        while True:
            position = await position_stream.__anext__()
            latitude_deg = position.latitude_deg
            longitude_deg = position.longitude_deg
            absolute_altitude_m = position.absolute_altitude_m

            await self.update_coordinates(latitude_deg, longitude_deg, absolute_altitude_m)
            await asyncio.sleep(0.1)

    def gps_coordinates(self) -> Coordinates:
        """現在の座標を取得"""
        return Coordinates(self.longitude_deg.value, self.latitude_deg.value, self.absolute_altitude_m.value)
    
    async def catch_gps(self)-> None:
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                    break 
                
    # async def Get_gps_info(self) -> None:
    #     async for gps_info in self.drone.telemetry.gps_info():
    #         self.num_satellites = gps_info.num_satellites
    #         self.fix_type = gps_info.fix_type

        