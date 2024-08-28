import sys
from pathlib import Path
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    asyncio.create_task(dronecontroller.lidar_test_loop())

if __name__ == "__main__":
    asyncio.run(main())
