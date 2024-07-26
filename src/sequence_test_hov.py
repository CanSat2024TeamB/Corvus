import asyncio
from drone.drone_controller import DroneController

async def main():
    drone = DroneController()

    await drone.connect()
    await drone.arm()
    asyncio.create_task(drone.invoke_sensor())

    # 5秒待機してから新しいタスクを追加
    await asyncio.sleep(5)
    await drone.add_sequence_task(drone.sequence_test_hovering())

    # メインループを続けるために、永続的に動作させる
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())