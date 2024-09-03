import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from drone.drone_controller import DroneController
import logger.flight_log as flight_log

async def main():
    drone = DroneController()

    await drone.connect()
    await drone.arm()
    drone.invoke_sensor()

    flight_log.start(drone.get_logger_instance(), drone.get_position_manager_instance())

    # 5秒待機してから新しいタスクを追加
    await asyncio.sleep(5)
    await drone.add_sequence_task(drone.sequence_test_precise_land())

    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())