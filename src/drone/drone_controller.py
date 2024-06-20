import asyncio
from mavsdk import System
from sensor import lidar_handler
from control import position_manager
from flight import flight_controller

class DroneController:
    def __init__(self):
        self.drone = System()
        self.set_up()

    def set_up(self) -> None:
        self.lidar_handler = lidar_handler.LiDARHandler(self.drone)
        self.position_manager = position_manager.PositionManager(self.drone, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.flight_controller = flight_controller.FlightController(self)
        return

    def drone(self):
        return self.drone
    
    async def invoke_sensor(self) -> None:
        async with asyncio.TaskGroup() as task_group:
            lidar_invoke = task_group.create_task(self.lidar_handler.invoke())
