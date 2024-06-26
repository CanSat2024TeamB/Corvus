import asyncio
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

def main():
    config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    config = ConfigManager(config_path)
    drone = DroneController()

    speed = 6.111
    target_coordinates = Coordinates()


    asyncio.run(drone.set_up())
    asyncio.run(drone.invoke_sensor_and_sequence(drone.sequence_test_mission(speed,target_coordinates)))
    return

if __name__ == "__main__":
    main()