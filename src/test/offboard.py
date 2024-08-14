import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from drone.drone_controller import DroneController
from mavsdk.offboard import (OffboardError, PositionNedYaw, VelocityNedYaw, VelocityBodyYawspeed)
import asyncio
import math

import time
import datetime

from threading import Thread

def record_alt(drone_controller: DroneController):
    while True:
        altitude = drone_controller.position_manager.raw_altitude()
        yaw_deg = drone_controller.position_manager.yaw_deg()
        drone_controller.get_logger_instance().write(f"{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}", altitude, yaw_deg)
        time.sleep(0.1)

async def run():
    drone_controller = DroneController()
    logger = drone_controller.get_logger_instance()

    await drone_controller.connect()
    await drone_controller.arm()

    await asyncio.sleep(1)
    await drone_controller.add_sequence_task(drone_controller.sequence_test_precise_land())

    print("drone taking off")
    logger.write("drone taking off")
    await drone_controller.flight_controller.takeoff(3)
    await drone_controller.flight_controller.hovering(3)

    drone = drone_controller.get_drone_instance()

    print("initializing offbord mode")
    logger.write("initializing offbord mode")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0))

    print("starting offboard controll")
    logger.write("starting offboard controll")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(error._result.result)

    print("ascending 3 m")
    logger.write("ascending 3 m")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 0))
    await asyncio.sleep(5)
        
    print("start_turning")
    logger.write("start_turning")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 20))
    #await drone.offboard.set_position_ned(PositionNedYaw(5.0, 0.0, -2.0, 0.0))
    await asyncio.sleep(10)
    print("reached target")
    logger.write("reached target")
    
    # yaw_deg = drone_controller.position_manager.yaw_deg()
    # yaw_rad = yaw_deg * math.pi / 180
    # await drone.offboard.set_velocity_body(VelocityBodyYawspeed(math.cos(yaw_rad) * 0.1, math.sin(yaw_rad) * 0.1, 1 * 0.1, 0))
    # await asyncio.sleep(20)

    await drone.offboard.stop()
    print("stopped offboard controll")
    logger.write("stopped offboard controll")

if __name__ == "__main__":
    record_alt_thread = Thread(target = record_alt, daemon = True)
    record_alt_thread.start()
    asyncio.run(run())