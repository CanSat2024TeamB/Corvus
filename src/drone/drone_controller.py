import asyncio
from mavsdk import System
from sensor import lidar_handler
from control import position_manager
from flight import flight_controller

class DroneController:
    pixhawk_address: str = "serial:///dev/ttyACM0:115200"

    def __init__(self):
        self.drone = System()
        self.lidar_handler = lidar_handler.LiDARHandler(self.drone)
        self.gps_handler = None
        self.compass_handler = None
        self.position_manager = position_manager.PositionManager(self.drone, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.flight_controller = flight_controller.FlightController(self)

    def drone(self):
        return self.drone

    async def set_up(self) -> None:
        await self.connect()
        await self.arm()
        return
    
    async def connect(self) -> bool:
        print("Connecting...")
        await self.drone.connect(system_address = self.pixhawk_address)

        print("Waiting for drone to connect...")
        async for state in drone.core.connection_state():
            if state.is_connected:
                print(f"Connected to drone!")
                break
            await asyncio.sleep(0.1)

        return True
    
    async def arm(self) -> bool:
        print("Waiting for drone to be armable...")
        async for is_armable in drone.telemetry.health():
            if is_armable:
                print("Drone is armable")
                break
            await asyncio.sleep(0.11)

        print("Arming the drone...")
        await drone.action.arm()

        async for is_armed in drone.telemetry.armed():
            if is_armed:
                print("drone is armed")
                break
            await asyncio.sleep(0.1)
        
        return True
    
    async def invoke_sensor(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            lidar_invoke = task_group.create_task(self.lidar_handler.invoke())
