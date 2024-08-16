import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from drone.gazebo_drone_controller import GazeboDroneController
from control.coordinates import Coordinates

async def run():
    drone: GazeboDroneController = GazeboDroneController()

    await drone.connect()

    asyncio.create_task(drone.invoke_sensor())

    await drone.arm()
    await drone.flight_controller.takeoff(5)
    await drone.flight_controller.hovering(5)
    await drone.flight_controller.go_to_location(8, Coordinates(139.986, 40.14324473, 5))
    print("reached target point")
    await drone.flight_controller.land()

async def test_lidar():
    drone: GazeboDroneController = GazeboDroneController()
    await drone.connect()

    async for distance_sensor in drone.get_drone_instance().telemetry.distance_sensor():
        max_dinstance = distance_sensor.maximum_distance_m
        min_distance = distance_sensor.minimum_distance_m
        lidar = distance_sensor.current_distance_m
        print("max:", max_dinstance, "min:", min_distance, "now:", lidar)

async def test_gps():
    drone: GazeboDroneController = GazeboDroneController()
    await drone.connect()

    async for data in drone.get_drone_instance().telemetry.raw_gps():
        print(data)

if __name__ == "__main__":
    asyncio.run(run())