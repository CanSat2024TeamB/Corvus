import asyncio
from mavsdk import System
from sensor.lidar_handler import LiDARHandler
from control.coordinates import Coordinates
from control.battery import Battery_watch
from control.gps_handler import GPSHandler
from control.position_manager import PositionManager
from control.compass_handler import CompassHandler
from flight.flight_controller import FlightController
from logger.logger import Logger
from sensor.acceleration_velocity import Acceleration_Velocity


class DroneController:
    pixhawk_address: str = "serial:///dev/ttyACM0:115200"
    #pixhawk_address: str = "udp://:14540"

    def __init__(self):
        self.drone_instance = System()
        #self.drone = System(mavsdk_server_address='localhost', port=50051)
        self.lidar_handler = LiDARHandler(self.drone_instance)
        self.gps_handler = GPSHandler(self.drone_instance)
        self.battery_watch = Battery_watch(self.drone_instance)
        self.compass_handler = CompassHandler(self.drone_instance)
        self.position_manager = PositionManager(self.drone_instance, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.flight_controller = FlightController(self.drone_instance, self.position_manager)
        self.logger = Logger()
        self.ac_vel = Acceleration_Velocity(self.drone_instance)

        self.task_group = None
       

    def get_drone_instance(self):
        return self.drone_instance
    
    def get_position_manager_instance(self):
        return self.position_manager

    
    async def connect(self) -> bool:
        print("Connecting...")
        await self.drone_instance.connect(system_address = self.pixhawk_address)

        print("Waiting for drone to connect...")
        async for state in self.drone_instance.core.connection_state():
            if state.is_connected:
                print(f"Connected to drone!")
                break
            await asyncio.sleep(0.1)

        return True
    
    
    async def arm(self) -> bool:
        print("Waiting for drone to be armable...")
        async for is_armable in self.drone_instance.telemetry.health():
            if is_armable:
                print("Drone is armable")
                break
            await asyncio.sleep(0.11)

        print("Arming the drone...")
        await self.drone_instance.action.arm()

        async for is_armed in self.drone_instance.telemetry.armed():
            if is_armed:
                print("drone is armed")
                break
            await asyncio.sleep(0.1)
        
        return True
    
    async def logger_write(self):
        while True:
            await asyncio.sleep(1)
            message_1 = str(self.position_manager.adjusted_altitude())
            message_2 = str(self.position_manager.adjusted_coordinates_lon())
            message_3 = str(self.position_manager.adjusted_coordinates_lat())

            #message_4 = str(self.ac_vel.get_velocity())
            #message_5 = str(self.battery_watch.remaining_percent())
            #message_6 = str(self.battery_watch.voltage_v())
            #message_7 = str(self.battery_watch.temperature_degc())
            self.logger.write(message_1,message_2,message_3,)


    
    async def sequence_test_hovering(self):
        await self.flight_controller.takeoff(3)
        print('reached start hovering')
        await self.flight_controller.hovering(10)
        print('finish hovering start landing')
        await self.flight_controller.land()
       # await self.flight_controller.disarm()

    async def sequence_test_mission(self,speed, *target_coordinates: Coordinates):
        await self.flight_controller.go_to(speed, *target_coordinates)
        print('mission started')
        while True:
            await asyncio.sleep(0.1)
            mission_completed = await self.flight_controller.if_mission_finished()
            if mission_completed:
                print('mission finished start hovering')
                await self.flight_controller.hovering(10)
                print(' hovering finished start landing')
                await self.flight_controller.land()
                print('landed')
                # await self.flight_controller.disarm()
                break

    async def sequence_test_goto(self,speed, yaw_deg, target_coordinates: Coordinates):
        await self.flight_controller.takeoff(3)
        print('reached')
        print('goto started')
        await self.flight_controller.go_to_location(speed, yaw_deg, target_coordinates)
        print('goto finished start hovering')
        await self.flight_controller.hovering(10)
        print(' hovering finished start landing')
        await self.flight_controller.land()
        print('landed')
        # await self.flight_controller.disarm()

    async def sequence_test_endurance(self,speed, *target_coordinates: Coordinates): #要書き換え
        await self.flight_controller.takeoff(3)
        await self.flight_controller.hovering(10)
        await self.flight_controller.go_to(speed, *target_coordinates)
        while True:
            await asyncio.sleep(1)
            if self.battery_watch.remaining_percent()<35:
                await self.flight_controller.hovering(10)
                await self.flight_controller.land()
              #  await self.flight_controller.disarm()

    
    async def invoke_sensor(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            self.task_group = task_group  # TaskGroupの参照を保存
            task_group.create_task(self.lidar_handler.invoke_loop())
            task_group.create_task(self.gps_handler.invoke_loop())
            # task_group.create_task(self.battery_watch.invoke_loop())
            task_group.create_task(self.compass_handler.invoke_loop())
            # task_group.create_task(self.flight_controller.invoke_loop())
            task_group.create_task(self.logger_write())

    async def add_sequence_task(self, coro):
        if hasattr(self, 'task_group') and self.task_group:
            self.task_group.create_task(coro)
        else:
            print("No task group available to add the task.")
