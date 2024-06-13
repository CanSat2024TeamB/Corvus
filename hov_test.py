import asyncio
from mavsdk import System


async def run():
    # Create a drone object
    drone = System()
    
    # Connect to the drone
    print("connecting now")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")


    # Wait for the drone to connect
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone!")
            break

    #await drone.action.hold()


    # Check if drone is armable

    print("Waiting for drone to be armable...")
    async for is_armable in drone.telemetry.health():
        if is_armable:
            print("Drone is armable")
            break
        await asyncio.sleep(1)

    # Arm the drone
    print("Arming the drone...")
    await drone.action.arm()

    async for is_armed in drone.telemetry.armed():
        if is_armed:
            print("drone is armed")
            break

    
    await drone.action.takeoff()
    while drone.Lidar <= 1.5:
        await asyncio.sleep(0.5)
    await drone.action.hold()
    await asyncio.sleep(5)
    await drone.action.land()  

if __name__ == "__main__":
    asyncio.run(run())

 