import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from drone.drone_controller import DroneController
from mavsdk.offboard import (OffboardError, PositionNedYaw, VelocityNedYaw, VelocityBodyYawspeed)
import asyncio

import time
import datetime

from threading import Thread, Condition

drone_controller = DroneController()
condition = Condition()

def record_alt():
    global drone_controller
    logger = drone_controller.get_logger_instance()
    while True:
        altitude = drone_controller.position_manager.raw_altitude()
        yaw_deg = drone_controller.position_manager.yaw_deg()
        
        condition.acquire()
        logger.write(f"{datetime.datetime.now().strftime('%f')}", f"alt: {altitude}, yaw: {yaw_deg}")
        condition.release()

        time.sleep(0.1)

async def run():
    global drone_controller
    logger = drone_controller.get_logger_instance()

    condition.acquire()
    logger.write("start sequence")
    condition.release()

    await drone_controller.connect()
    await drone_controller.arm()

    await asyncio.sleep(1)

    print("drone taking off")

    condition.acquire()
    logger.write("drone taking off")
    condition.release()
    
    await drone_controller.flight_controller.takeoff(1)
    print("hovering...")
    await drone_controller.flight_controller.hovering(3)
    print("end hovering")

    drone = drone_controller.get_drone_instance()

    print("initializing offbord mode")

    condition.acquire()
    logger.write("initializing offbord mode")
    condition.release()

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0))

    print("starting offboard controll")

    condition.acquire()
    logger.write("starting offboard controll")
    condition.release()

    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(error._result.result)

    print("ascending 5 m")

    condition.acquire()
    logger.write("ascending 0.5 m")
    condition.release()

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -0.5, 0))
    await asyncio.sleep(5)
        
    print("start_turning")

    condition.acquire()
    logger.write("start_turning")
    condition.release()

    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 20))
    #await drone.offboard.set_position_ned(PositionNedYaw(5.0, 0.0, -2.0, 0.0))
    await asyncio.sleep(10)
    print("reached target")

    condition.acquire()
    logger.write("reached target")
    condition.release()
    
    # yaw_deg = drone_controller.position_manager.yaw_deg()
    # yaw_rad = yaw_deg * math.pi / 180
    # await drone.offboard.set_velocity_body(VelocityBodyYawspeed(math.cos(yaw_rad) * 0.1, math.sin(yaw_rad) * 0.1, 1 * 0.1, 0))
    # await asyncio.sleep(20)

    await drone.offboard.stop()
    print("stopped offboard controll")

    condition.acquire()
    logger.write("stopped offboard controll")
    condition.release()

    await drone.action.land()

if __name__ == "__main__":
    record_alt_thread = Thread(target = record_alt, daemon = True)
    record_alt_thread.start()
    asyncio.run(run())