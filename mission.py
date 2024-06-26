import asyncio
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)

lidar = -1
drone = System()


async def set_up():
    global drone

    # Connect to the drone
    print("connecting now")
    await drone.connect(system_address="serial:///dev/ttyACM0:115200")

    # Wait for the drone to connect
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Connected to drone!")
            break

    #await drone.action.hold()

    # Check if drone is armable

    print("Waiting for drone to be armable...")
    async for is_armable in drone.telemetry.health():
        if is_armable:
            print("Drone is armable")
            break
        await asyncio.sleep(1)

    # Arm the drone
    print("Arming the drone...")
    await drone.action.arm()

    async for is_armed in drone.telemetry.armed():
        if is_armed:
            print("drone is armed")
            break

async def update_lidar():
    global lidar
    async for distance_sensor in drone.telemetry.distance_sensor():
        lidar = distance_sensor.current_distance_m

async def Get_position():
    async for position in drone.telemetry.position():
        drone.Latitude_deg = position.latitude_deg
        drone.Longitude_deg = position.longitude_deg
        drone.Absolute_altitude_m = position.absolute_altitude_m
        drone.Relative_altitude_m = position.relative_altitude_m
        if drone.Reboot_flag:
            return
        
async def flight():
    print_mission_progress_task = asyncio.ensure_future(print_mission_progress(drone))

    running_tasks = [print_mission_progress_task]
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, running_tasks))

    
    # Define home position
    home_lat = drone.Latitude_deg
    home_lon = drone.Longitude_deg

    target_lon=35.7149956
    target_lat=139.7605576
    

    mission_items = []
    mission_items.append(MissionItem(home_lat,
                                     home_lon,
                                     1,
                                     10,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))
    mission_items.append(MissionItem(target_lon,
                                     target_lat,
                                     1,
                                     10,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))


    mission_plan = MissionPlan(mission_items)

    await drone.mission.set_return_to_launch_after_mission(False) #ミッション終了後に離陸地点に戻るか

    print("-- Uploading mission")
    await drone.mission.upload_mission(mission_plan)

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Starting mission")
    await drone.mission.start_mission()


    
async def print_mission_progress(drone):
    async for mission_progress in drone.mission.mission_progress():
        print(f"Mission progress: "
              f"{mission_progress.current}/"
              f"{mission_progress.total}")

async def observe_is_in_air(drone, running_tasks):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            for task in running_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
            await asyncio.get_event_loop().shutdown_asyncgens()

            return

        
async def main():
    await set_up()
    async with asyncio.TaskGroup() as task_group:
        lidar_task = task_group.create_task(update_lidar())
        gps_task = task_group.create_task(Get_position())
        flight_task = task_group.create_task(flight())


if __name__ == "__main__":
    asyncio.run(main())











    
