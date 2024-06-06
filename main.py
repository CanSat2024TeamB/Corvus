import asyncio
from mavsdk import System


async def run():
    # Create a drone object
    drone = System()
    
    # Connect to the drone
    await drone.connect(system_address="serial:///dev/serial0:57600")

    # Wait for the drone to connect
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone!")
            break

    # Check if drone is armable
    print("Waiting for drone to be armable...")
    async for is_armable in drone.telemetry.is_armable():
        if is_armable:
            print("Drone is armable")
            break
        await asyncio.sleep(1)

    # Arm the drone
    print("Arming the drone...")
    await drone.action.arm()
    # Wait for a few seconds before disarming
    await asyncio.sleep(10)

    # Disarm the drone
    print("Disarming the drone...")
    await drone.action.disarm()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
