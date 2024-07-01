import mavsdk
import asyncio

class Battery_watch:
    def __init__(self,drone):
        self.drone = drone
        self.voltage_v: float = 0
        self.current_battery_a: float = 0
        self.remaining_percent: float = 0
        

    def battery_info_update(self,info) -> None:
        self.voltage_v = info.voltage_v
        self.current_battery_a = info.current_battery_a
        self.remaining_percent = info.remaining_percent
        self.temperature_degc = info.temperature_degc
#################################################以下がオープン
    async def invoke_loop(self) -> None:
        async for info in self.drone.telemetry.battery():
            self.battery_info_update(info)
            await asyncio.sleep(1)

    def voltage_v(self) -> float:
        return self.voltage_v
    
    def current_battery_a(self) -> float:
        return self.current_battery_a
    
    def remaining_percent(self) -> float:
        return self.remaining_percent
    
    def temperature_degc(self) -> float:
        return self.temperature_degc