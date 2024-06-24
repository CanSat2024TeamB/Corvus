import asyncio
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

def main():
    config_path: str = ""
    config = ConfigManager("assets/config/config.ini")
    drone = DroneController()

    asyncio.run(drone.set_up())
    return

if __name__ == "__main__":
    main()