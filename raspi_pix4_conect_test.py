import asyncio
from mavsdk import System
import serial.tools.list_ports

drone = System()

async def set_up():
    global drone
    ports = serial.tools.list_ports.comports()
    print(ports)
    # Connect to the drone
    print("connecting now")
    await drone.connect(system_address="serial:///dev/ttyACM1:115200")

    # Wait for the drone to connect
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone!")
            break

if __name__ == "__main__":
    asyncio.run(set_up())
