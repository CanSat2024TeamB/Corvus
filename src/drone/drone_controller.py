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
from wire.wirehandler import WireHandler

class DroneController:
    pixhawk_address: str = "serial:///dev/ttyACM0:115200"
    #pixhawk_address: str = "udp://:14540"

    def __init__(self):
        self.drone = System()
        #self.drone = System(mavsdk_server_address='localhost', port=50051)
        self.lidar_handler = LiDARHandler(self.drone)
        self.gps_handler = GPSHandler(self.drone)
        self.battery_watch = Battery_watch(self.drone)
        self.compass_handler = CompassHandler(self.drone)
        self.position_manager = PositionManager(self.drone, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.flight_controller = FlightController(self.drone, self.position_manager)
        self.logger = Logger()
        self.wirehandler = WireHandler()

        self.para_pin_no = 7

        self.para_duration = 5

    def drone(self):
        return self.drone
    
    def position_manager(self):
        return self.position_manager

    async def set_up(self) -> None:
        await self.connect()
        await self.arm()
        return
    
    async def connect(self) -> bool:
        print("Connecting...")
        await self.drone.connect(system_address = self.pixhawk_address)

        print("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print(f"Connected to drone!")
                break
            await asyncio.sleep(0.1)

        return True
    
    async def arm(self) -> bool:
        print("Waiting for drone to be armable...")
        async for is_armable in self.drone.telemetry.health():
            if is_armable:
                print("Drone is armable")
                break
            await asyncio.sleep(0.11)

        print("Arming the drone...")
        await self.drone.action.arm()

        async for is_armed in self.drone.telemetry.armed():
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
            self.logger.write(message_1,message_2,message_3)

    def para_case_stand_nichrome(self):
        self.wirehandler.nichrome_cut(self.para_pin_no, self.para_duration)
    
    async def sequence_test_hovering(self):
        await self.flight_controller.takeoff()
        print('taking off')
        await self.flight_controller.set_altitude(1.0)
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

    async def sequence_test_endurance(self,speed, *target_coordinates: Coordinates):
        await self.flight_controller.takeoff()
        await self.flight_controller.set_altitude(1.0)
        await self.flight_controller.hovering(10)
        await self.flight_controller.go_to(speed, *target_coordinates)
        while True:
            await asyncio.sleep(1)
            if self.battery.remaining_percent()<35:
                await self.flight_controller.hovering(10)
                await self.flight_controller.land()
              #  await self.flight_controller.disarm()

    
    async def invoke_sensor_and_sequence(self,sequence) -> None:
        async with asyncio.TaskGroup() as task_group:
            lidar_invoke = task_group.create_task(self.lidar_handler.invoke_loop())
            gps_invoke = task_group.create_task(self.gps_handler.invoke_loop())
            battery_invoke = task_group.create_task(self.battery_watch.invoke_loop())
            compass_invoke = task_group.create_task(self.compass_handler.invoke_loop())
            in_air_invoke = task_group.create_task(self.flight_controller.invoke_loop())
            sequence_loop = task_group.create_task(sequence)
            logger_invoke =task_group.create_task(self.logger_write())

# ^^^^^各クラスのコンストラクタに移譲^^^^^^