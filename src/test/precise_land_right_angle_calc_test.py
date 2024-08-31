import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    await dronecontroller.connect()
    asyncio.create_task(dronecontroller.camera_calc_test_loop2())
    await asyncio.sleep(5)
    await dronecontroller.add_sequence_task(dronecontroller.sequence_test_goto_and_precise_land_right_angle_calc_test())
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")


if __name__ == "__main__":
    asyncio.run(main())