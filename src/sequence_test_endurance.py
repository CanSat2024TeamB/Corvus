import asyncio
from pathlib import Path
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
    #await drone.arm()
    await asyncio.sleep(5)

    num = 2
    speed = 2
    first_lon = drone.position_manager.adjusted_coordinates_lon()
    first_lat = drone.position_manager.adjusted_coordinates_lat()
    hov_alt = 3
    target_coordinates_1 = Coordinates(140.1081125,35.7700173,hov_alt)
    target_coordinates_2 = Coordinates(140.1080039,35.7704584,hov_alt)
    args = [speed] + [target for pair in zip([target_coordinates_1] * num, [target_coordinates_2] * num) for target in pair]


    await drone.arm()
    await drone.add_sequence_task(drone.sequence_test_endurance(*args))
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")


if __name__ == "__main__":
    asyncio.run(main())