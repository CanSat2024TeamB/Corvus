import asyncio
from config import config_manager
from drone import drone_controller

def main():
    config_path: str = ""
    config = config_manager.ConfigManager("assets/config/config.ini")
    drone = drone_controller.DroneController()

    asyncio.run(drone.set_up())
    return

if __name__ == "__main__":
    main()