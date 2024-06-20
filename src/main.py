from config import config_manager
from drone import drone_controller

def main():
    config_path: str = ""
    config = config_manager.ConfigManager("")
    drone_controller = drone_controller.DroneController()
    return

if __name__ == "__main__":
    main()