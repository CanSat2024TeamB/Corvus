import asyncio
from mavsdk.mission import (MissionItem, MissionPlan)

class FlightController:
    get_altitude_interval: float = 0.01

    def __init__(self, drone_controller):
        self.drone_controller: DroneController = drone_controller

        self.drone: System = self.drone_controller.drone()
        self.position_manager: PositionManager = self.drone.position_manager()
        
        self.is_in_air: bool = False
        asyncio.run(self.invoke_loop())
    
    async def takeoff(self) -> bool:
        await self.drone.action.takeoff()
        return True

    async def set_altitude(self, altitude: float) -> bool:
        while self.position_manager.altitude() <= altitude:
            await asyncio.sleep(get_height_interval)
        return True
    
    async def go_to(self, *target_coordinates: "*Coordinates") -> bool:
        #position = self.position_manager
        mission_items = []
        mission_items.append(MissionItem(position.latitude, position.longitude, 1, 10, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
        for coordinates in target_coordinates:
            mission_items.append(MissionItem(coordinates.latitude, coordinates.longitude, 1, 10, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
        mission_plan = MissionPlan(mission_items)
        await self.execute_mission(mission_plan)
        return True

    async def land(self) -> bool:
        await self.drone.action.land()
        return True
    
    async def execute_mission(self, mission_plan: MissionPlan) -> bool:
        await self.drone.mission.upload_mission(mission_plan)
        async for health in self.drone.telemetry.health():
            if health.is_global_posision_op and health.is_home_position_ok:
                break
        return True
    
    def update_is_in_air(self, is_in_air: bool) -> None:
        self.is_in_air = is_in_air
        return
    
    async def invoke_loop(self) -> None:
        async for is_in_air in self.drone.telemetry.in_air():
            update_is_in_air(is_in_air)