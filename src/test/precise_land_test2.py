import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from drone.drone_controller import DroneController
from control.coordinates import Coordinates
import logger.flight_log as flight_log

async def sequence(drone: DroneController, speed, target_coordinates):
    logger = drone.get_logger_instance()
    print("taking off")
    await drone.flight_controller.takeoff(5)
    print("finished taking off")
    await drone.flight_controller.hovering(5)
    print("going to the target position")
    await drone.flight_controller.go_to_location(speed, target_coordinates, 0.5)
    print("start precise landing")
    result = await drone.flight_controller.offboard_precise_land()
    if not result:
        await drone.flight_controller.go_to_location(speed, target_coordinates, 0.5)
        print("starting vertical land")
        await drone.flight_controller.land()
    print("landed")

async def main():
    SPEED = 8
    TARGET = Coordinates(longitude=000.0000, latitude=000.0000, altitude=5)

    drone = DroneController()

    await drone.connect()
    await drone.arm()
    drone.invoke_sensor()

    flight_log.start(drone.get_logger_instance(), drone.get_position_manager_instance())

    # 1秒待機してから新しいタスクを追加
    await asyncio.sleep(1)
    await drone.add_sequence_task(sequence(drone, SPEED, TARGET))

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())