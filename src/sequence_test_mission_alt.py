import asyncio
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from drone.drone_controller import DroneController

async def main():
    # config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    # config = ConfigManager(config_path)
    
    # ドローンコントローラのインスタンスを作成
    drone = DroneController()
    
    # ドローンに接続
    await drone.connect()
    
    # センサーを起動
    asyncio.create_task(drone.invoke_sensor())

    # 少し待機して位置情報を取得
    await asyncio.sleep(5)
    
    speed = 1.0
    first_lon = drone.position_manager.adjusted_coordinates_lon()
    first_lat = drone.position_manager.adjusted_coordinates_lat()
    hov_alt = 2
    target_coordinates_1 = Coordinates(first_lon, first_lat, hov_alt)
    
    # 任務を追加する
    await  drone.add_sequence_task(drone.sequence_test_mission(speed, target_coordinates_1))
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")

if __name__ == "__main__":
    asyncio.run(main())
