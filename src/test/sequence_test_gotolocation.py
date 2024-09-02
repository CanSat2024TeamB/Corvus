import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

async def main():
    # config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    # config = ConfigManager(config_path)
    drone = DroneController()
    await drone.connect()
    
    # `invoke_sensor`の呼び出し
    asyncio.create_task(drone.invoke_sensor())

    # すぐに`invoke_sensor`タスクを開始する
    await asyncio.sleep(1)

    speed = 3.0
    target_coordinates = Coordinates(140.10804658799998, 35.770481484, 5.0)

    # `add_sequence_task`の呼び出し
    await drone.add_sequence_task(drone.sequence_test_goto(speed, target_coordinates))

    try:
        # 無限ループを維持するためのFutureを作成
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())
