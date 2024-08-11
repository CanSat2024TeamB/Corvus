import asyncio
import mavsdk
from control.coordinates import Coordinates  


class GPSHandler:
    def __init__(self, drone):
        self.drone = drone
        self.coordinates = Coordinates()

    async def update_coordinates(self, latitude_deg, longitude_deg, absolute_altitude_m) -> None:
        """最新のGPSデータで座標を更新"""
        self.coordinates.set_latitude(latitude_deg)
        self.coordinates.set_longitude(longitude_deg)
        self.coordinates.set_altitude(absolute_altitude_m)
        return

    async def invoke_loop(self) -> None:
        position_stream = self.drone.telemetry.position()

        while True:
            position = await position_stream.__anext__()
            latitude_deg = position.latitude_deg
            longitude_deg = position.longitude_deg
            absolute_altitude_m = position.absolute_altitude_m

            await self.update_coordinates(latitude_deg, longitude_deg, absolute_altitude_m)
            print(f"Latitude: {latitude_deg}, Longitude: {longitude_deg}, Altitude AMSL: {absolute_altitude_m}")
            await asyncio.sleep(0.05)

    def get_coordinates(self) -> Coordinates:
        """現在の座標を取得"""
        return self.coordinates

    