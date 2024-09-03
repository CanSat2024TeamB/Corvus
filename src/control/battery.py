import mavsdk
import asyncio

import multiprocessing

class Battery_watch:
    def __init__(self,drone):
        self.drone = drone
        self.voltage: float = multiprocessing.Value("f", 0.0)
        self.current_battery: float = multiprocessing.Value("f", 0.0)
        self.remaining: float = multiprocessing.Value("f", 0.0)
        self.temperature: float = multiprocessing.Value("f", 0.0)
        

    def battery_info_update(self, info) -> None:
        self.voltage.value = info.voltage_v
        self.current_battery.value = info.current_battery_a
        self.remaining.value = info.remaining_percent
        self.temperature.value = info.temperature_degc
#################################################以下がオープン
    async def invoke_loop(self) -> None:
        async for info in self.drone.telemetry.battery():
            self.battery_info_update(info)
            print('updated')
            await asyncio.sleep(1)

    def voltage_v(self) -> float:
        return self.voltage.value
    
    def current_battery_a(self) -> float:
        return self.current_battery.value
    
    def remaining_percent(self) -> float:
        return self.remaining.value
    
    def temperature_degc(self) -> float:
        return self.temperature.value