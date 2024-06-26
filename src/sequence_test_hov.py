import asyncio
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

async def main():
    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    drone = DroneController()

    await drone.set_up()
    await drone.invoke_sensor_and_sequence(drone.sequence_test_hovering())
    

if __name__ == "__main__":
    main()