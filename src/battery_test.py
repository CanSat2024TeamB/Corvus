from control.battery import Battery_watch
import asyncio
from drone.drone_controller import DroneController

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    
    await dronecontroller.connect()
    battery = Battery_watch(drone)
    await asyncio.create_task(battery.invoke_loop())
    print(battery.voltage_v())
    print(battery.remaining_percent())
    print(battery.current_battery_a())

asyncio.run(main())