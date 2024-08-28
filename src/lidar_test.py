import sys
from pathlib import Path
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    await dronecontroller.connect()
    asyncio.create_task(dronecontroller.lidar_test_loop())
    await asyncio.sleep(float('inf'))

if __name__ == "__main__":
    asyncio.run(main())
