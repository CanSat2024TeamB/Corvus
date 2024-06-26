import asyncio
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

async def main():
    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    drone = DroneController()

    speed = 1.0
    target_coordinates = Coordinates(139.760557,35.714995,0)


    await drone.set_up()
    await drone.invoke_sensor_and_sequence(drone.sequence_test_mission(speed,target_coordinates))
    return

if __name__ == "__main__":
    asyncio.run(main())