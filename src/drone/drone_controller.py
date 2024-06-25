import asyncio
from mavsdk import System
from sensor.lidar_handler import LiDARHandler
from control.gps_handler import GPSHandler
from control.compass_handler import CompassHandler
from control.position_manager import PositionManager
from flight.flight_controller import FlightController

class DroneController:
    pixhawk_address: str = "serial:///dev/ttyACM0:115200"
    #pixhawk_address: str = "udp://:14540"

    def __init__(self):
        self.drone = System()
        #self.drone = System(mavsdk_server_address='localhost', port=50051)
        self.lidar_handler = LiDARHandler(self.drone)
        self.gps_handler = GPSHandler(self.drone)
        self.compass_handler = CompassHandler(self.drone)
        self.position_manager = PositionManager(self.drone, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.flight_controller = FlightController(self.drone, self.position_manager)

    def drone(self):
        return self.drone
    
    def position_manager(self):
        return self.position_manager

    async def set_up(self) -> None:
        await self.connect()
        print("Checking GPS Connection...")
        await self.gps_handler.catch_gps()
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
    
    async def test_hovering(self):
        await self.flight_controller.take_off()
        await self.flight_controller.set_altitude(1.0)
        await self.flight_controller.hovering(10)
        await self.flight_controller.land()

    
#    async def invoke_sensor(self) -> None:
#        async with asyncio.TaskGroup() as task_group:
#            lidar_invoke = task_group.create_task(self.lidar_handler.invoke())
# ^^^^^各クラスのコンストラクタに移譲^^^^^^