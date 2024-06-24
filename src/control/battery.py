import mavsdk
import asyncio

class Battery:
    def __init__(self,drone):
        self.drone = drone
        self.voltage_v: float = None
        self.current_battery_a: float = None
        self.remaining_percent: float = None


    def battery_info_update(self,info) -> None:
        self.voltage_v = info.voltage_v
        self.current_battery_a = info.current_battery_a
        self.remaining_percent = info.remaining_percent

    async def battery_info(self) -> None:
        async for info in self.telemetry.battery:
            self.update_info_update(info)
            await asyncio.sleep(10)

#################################################以下がオープン