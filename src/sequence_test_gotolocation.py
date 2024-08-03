import asyncio
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

async def main():
    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    drone = DroneController()
    await drone.connect()
    asyncio.create_task(drone.invoke_sensor())
    await asyncio.sleep(1)

    speed = 1.0
    target_coordinates = Coordinates(140.1080417,35.7702389,3)


    await drone.arm()
    await drone.add_sequence_task(drone.sequence_test_goto(speed,target_coordinates))
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())