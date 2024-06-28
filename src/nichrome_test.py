import asyncio
from drone.drone_controller import DroneController

async def main():
    drone = DroneController()

    await drone.para_case_stand_nichrome()

if __name__ == "__main__":
    asyncio.run(main())