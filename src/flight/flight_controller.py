import asyncio
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)

from control.position_manager import PositionManager
from control.coordinates import Coordinates

class FlightController:
    get_altitude_interval: float = 0.01

    def __init__(self, drone: System, position_manager: PositionManager):
        self.drone: System = drone
        self.position_manager: PositionManager = position_manager
        
        self.is_in_air: bool = False
        asyncio.run(self.invoke_loop())
    
    async def take_off(self) -> bool:
        await self.drone.action.takeoff()
        return True

    async def set_altitude(self, altitude: float) -> bool:
        while self.position_manager.altitude() <= altitude:
            await asyncio.sleep(FlightController.get_altitude_interval)
        return True
    
    async def hovering(self, time: float) -> bool:
        await self.drone.action.hold()
        await asyncio.sleep(time)
        return True
    
    async def go_to(self, speed, *target_coordinates: Coordinates) -> bool:
        mission_items = []
        for coordinates in target_coordinates:
            mission_items.append(MissionItem(coordinates.latitude(), coordinates.longitude(), coordinates.altitude(), speed, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
        
        mission_plan = MissionPlan(mission_items)

        await self.execute_mission(mission_plan)
        return True

    async def land(self) -> bool:
        await self.drone.action.land()
        return True
    
    async def execute_mission(self, mission_plan: MissionPlan) -> bool:
        await self.drone.mission.set_return_to_launch_after_mission(False)
        await self.drone.mission.upload_mission(mission_plan)
        await self.drone.mission.start_mission()
        return True
    
    async def if_mission_finished(self) -> bool:
        return await self.drone.mission.is_mission_finished()
    
    def update_is_in_air(self, is_in_air: bool) -> None:
        self.is_in_air = is_in_air
        return
    
    async def invoke_loop(self) -> None:
        async for is_in_air in self.drone.telemetry.in_air():
            self.update_is_in_air(is_in_air)