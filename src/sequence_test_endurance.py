import asyncio
from pathlib import Path
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

def main():
    config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    config = ConfigManager(config_path)
    drone = DroneController()
    
    num = 50
    speed = 6.111
    target_coordinates_1 = Coordinates()
    target_coordinates_2 = Coordinates()
    args = [speed] + [target for pair in zip([target_coordinates_1] * num, [target_coordinates_2] * num) for target in pair]


    asyncio.run(drone.set_up())
    asyncio.run(drone.invoke_sensor_and_sequence(drone.sequence_test_endurance(*args)))
    return

if __name__ == "__main__":
    main()