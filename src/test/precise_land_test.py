import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from drone.gazebo_drone_controller import GazeboDroneController

async def main():
    drone = GazeboDroneController()

    await drone.connect()
    await drone.arm()
    asyncio.create_task(drone.invoke_sensor())

    # 5秒待機してから新しいタスクを追加
    await asyncio.sleep(5)
    await drone.add_sequence_task(drone.sequence_test_precise_land())

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())