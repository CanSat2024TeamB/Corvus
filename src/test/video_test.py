import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import time
from drone.drone_controller import DroneController

async def run():
    drone = DroneController()
    await asyncio.sleep(5)

    print("start capturing")
    await drone.add_sequence_task(drone.capture_video_during_flight(1, None, "test.mp4", 10))

if __name__ == "__main__":
    asyncio.run(run())
