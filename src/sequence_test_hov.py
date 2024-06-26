import asyncio
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

def main():
    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    drone = DroneController()

    asyncio.run(drone.set_up())
    asyncio.run(drone.invoke_sensor_and_sequence(drone.sequence_test_hovering()))
    return

if __name__ == "__main__":
    main()