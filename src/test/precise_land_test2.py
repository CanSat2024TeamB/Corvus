import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from drone.drone_controller import DroneController
from control.coordinates import Coordinates
from config.config_manager import ConfigManager
import logger.flight_log as flight_log

async def sequence(drone: DroneController, speed, target_coordinates: Coordinates, goal_radius):
    logger = drone.get_logger_instance()
    logger.write("taking off")
    await drone.flight_controller.takeoff(5)
    logger.write("finished taking off")
    await drone.flight_controller.hovering(5)
    logger.write("going to the target position")
    await drone.flight_controller.go_to_location(speed, target_coordinates, goal_radius, margin_to_target=10)
    logger.write("start precise landing")
    result = await drone.flight_controller.offboard_precise_land()
    if not result:
        logger.write("failed precise landing, going above the target.")
        await drone.flight_controller.go_to_location(speed, target_coordinates, 0.5)
        logger.write("starting vertical land")
        await drone.flight_controller.land()
    logger.write("landed")

async def main():
    config = ConfigManager()
    section = "DEBUG"
    
    SPEED = config.read_float(section, "Speed")
    longitude = config.read_float(section, "TargetLon")
    latitude = config.read_float(section, "targetlat")
    hov_alt = config.read_float(section, "HovAlt")
    TARGET = Coordinates(longitude=longitude, latitude=latitude, altitude=hov_alt)
    GOAL_RADIUS = 0.5

    drone = DroneController()

    await drone.connect()
    await drone.arm()
    asyncio.create_task(drone.invoke_sensor())

    flight_log.start(drone.get_logger_instance(), drone.get_position_manager_instance())

    # 1秒待機してから新しいタスクを追加
    await asyncio.sleep(1)
    await drone.add_sequence_task(sequence(drone, SPEED, TARGET, GOAL_RADIUS))

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())