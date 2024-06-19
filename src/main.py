from config import config_manager
from drone import drone

def main():
    config_path: str = ""
    config = config_manager.ConfigManager("")
    drone = drone.Drone()
    return

if __name__ == "__main__":
    main()