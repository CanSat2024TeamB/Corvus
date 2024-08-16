import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from drone.gazebo_drone_controller import GazeboDroneController

async def run():
    drone: GazeboDroneController = GazeboDroneController()

    await drone.connect()
    await drone.arm()

    await drone.flight_controller.takeoff(5)
    await drone.flight_controller.hovering(5)
    await drone.flight_controller.land()

if __name__ == "__main__":
    asyncio.run(run())