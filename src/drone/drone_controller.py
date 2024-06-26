import asyncio
from mavsdk import System
from sensor.lidar_handler import LiDARHandler
from control.coordinates import Coordinates
from control.battery import Battery
from control.gps_handler import GPSHandler
from control.position_manager import PositionManager
from control.compass_handler import CompassHandler
from flight.flight_controller import FlightController
from logger.logger import Logger

class DroneController:
    pixhawk_address: str = "serial:///dev/ttyACM0:115200"
    #pixhawk_address: str = "udp://:14540"

    def __init__(self):
        self.drone = System()
        #self.drone = System(mavsdk_server_address='localhost', port=50051)
        self.lidar_handler = LiDARHandler(self.drone)
        self.gps_handler = GPSHandler(self.drone)
        self.battery = Battery(self.drone)
        self.compass_handler = CompassHandler(self.drone)
        self.position_manager = PositionManager(self.drone, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.flight_controller = FlightController(self.drone, self.position_manager)
        self.logger = Logger()

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
            message = str(self.position_manager.adjusted_altitude())
            self.logger.write(message)
    
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
        await self.flight_controller.take_off()
        await self.flight_controller.set_altitude(1.0)
        await self.flight_controller.hovering(10)
        await self.flight_controller.go_to(speed, *target_coordinates)
        while True:
            await asyncio.sleep(1)
            if self.flight_controller.if_mission_finished():
                await self.flight_controller.hovering(10)
                await self.flight_controller.land()
               # await self.flight_controller.disarm()

    async def sequence_test_endurance(self,speed, *target_coordinates: Coordinates):
        await self.flight_controller.take_off()
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
            #gps_invoke = task_group.create_task(self.gps_handler.invoke_loop())
            battery_invoke = task_group.create_task(self.battery.invoke_loop())
            compass_invoke = task_group.create_task(self.compass_handler.invoke_loop())
            in_air_invoke = task_group.create_task(self.flight_controller.invoke_loop())
            logger_invoke =task_group.create_task(self.logger_write())
            sequence_loop = task_group.create_task(sequence)

# ^^^^^各クラスのコンストラクタに移譲^^^^^^