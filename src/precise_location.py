import asyncio
from pathlib import Path
from statistics import mean, stdev
from drone.drone_controller import DroneController

async def main():
    drone = DroneController()
    await drone.connect()
    asyncio.create_task(drone.invoke_sensor())

    # すぐに`invoke_sensor`タスクを開始する
    await asyncio.sleep(1)

    lat_list = []
    lon_list = []

    for _ in range(100):
        lat = await drone.position_manager.adjusted_coordinates_lat()
        lon = await drone.position_manager.adjusted_coordinates_lon()
        lat_list.append(lat)
        lon_list.append(lon)

    # 平均値を計算
    lat_mean = mean(lat_list)
    lon_mean = mean(lon_list)

    # 標準偏差を計算
    lat_stdev = stdev(lat_list)
    lon_stdev = stdev(lon_list)

    # 結果を出力
    print(f"Latitude Mean: {lat_mean}, Latitude Standard Deviation: {lat_stdev}")
    print(f"Longitude Mean: {lon_mean}, Longitude Standard Deviation: {lon_stdev}")

if __name__ == "__main__":
    asyncio.run(main())
