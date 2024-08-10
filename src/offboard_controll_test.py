import asyncio
from drone.drone_controller import DroneController

async def main():
    drone = DroneController()

    await drone.connect()
    await drone.arm()
    #asyncio.create_task(drone.invoke_sensor())

    drone_instance = drone.get_drone_instance()
    
    try:
        await drone_instance.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: \
              {error._result.result}")
        print("-- Disarming")
        await drone_instance.action.disarm()
        return

    print("-- Go up at 70% thrust")
    await drone_instance.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.7))
    await asyncio.sleep(2)

    print("-- Roll 30 at 60% thrust")
    await drone_instance.offboard.set_attitude(Attitude(30.0, 0.0, 0.0, 0.6))
    await asyncio.sleep(2)

    print("-- Roll -30 at 60% thrust")
    await drone_instance.offboard.set_attitude(Attitude(-30.0, 0.0, 0.0, 0.6))
    await asyncio.sleep(2)

    print("-- Hover at 60% thrust")
    await drone_instance.offboard.set_attitude(Attitude(0.0, 0.0, 0.0, 0.6))
    await asyncio.sleep(2)

    print("-- Stopping offboard")
    try:
        await drone_instance.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: \
              {error._result.result}")

    await drone_instance.action.land()

if __name__ == "__main__":
    asyncio.run(main())