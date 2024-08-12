from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw, VelocityNedYaw, VelocityBodyYawspeed)
import asyncio
import math

async def run():
    drone = System()
    print("connecting drone...")
    await drone.connect(system_address="udp://:14550")

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("drone connected")
            break
    
    print("drone arming")
    await drone.action.arm()

    print("drone taking off")
    await drone.action.set_takeoff_altitude(5)
    await drone.action.takeoff()
    await asyncio.sleep(15)

    print("initializing offbord mode")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0))

    print("starting offboard controll")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(error._result.result)
    
    async for attitude in drone.telemetry.attitude_euler():
        print("yaw:", attitude.yaw_deg)
        break

    print("going to origin")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -5.0, 0))
    await asyncio.sleep(5)

    async for attitude in drone.telemetry.attitude_euler():
        print("yaw:", attitude.yaw_deg)
        break
        
    print("going 5 m north")
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(0, 0, 0, 20))
    #await drone.offboard.set_position_ned(PositionNedYaw(5.0, 0.0, -2.0, 0.0))
    await asyncio.sleep(15)
    print("reached target")

    yaw_deg = 0
    async for attitude in drone.telemetry.attitude_euler():
        print("yaw:", attitude.yaw_deg)
        yaw_deg = attitude.yaw_deg
        break
    
    yaw_rad = yaw_deg * math.pi / 180
    await drone.offboard.set_velocity_body(VelocityBodyYawspeed(math.cos(yaw_rad) * 0.1, math.sin(yaw_rad) * 0.1, 1 * 0.1, 0))
    await asyncio.sleep(20)

    await drone.offboard.stop()

if __name__ == "__main__":
    asyncio.run(run())