import sys
from pathlib import Path
import datetime

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

    lora = drone.get_lora_instance()
    await lora.lora_start()
    await asyncio.sleep(5)
    
    # `invoke_sensor`の呼び出し
    drone.invoke_sensor()

    # すぐに`invoke_sensor`タスクを開始する
    await asyncio.sleep(5)

    speed = 3.0
    target_coordinates = Coordinates(139.887311364, 35.766587931, 5)
    output_path = str(Path(__file__).parent.parent.parent.joinpath(f"assets/log/mov_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.mp4"))

    # `add_sequence_task`の呼び出し
    await drone.add_sequence_task(drone.capture_video_during_flight(speed, target_coordinates,output_path,30))

    try:
        # 無限ループを維持するためのFutureを作成
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())