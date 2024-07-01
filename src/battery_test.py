from control.battery import Battery_watch
import asyncio
from drone.drone_controller import DroneController

async def main():
    dronecontroller = DroneController()
    
    await dronecontroller.connect()
    await asyncio.create_task(dronecontroller.battery_watch.invoke_loop())
    print(dronecontroller.battery_watch.voltage_v())
    print(dronecontroller.battery_watch.remaining_percent())
    print(dronecontroller.battery_watch.current_battery_a())

asyncio.run(main())