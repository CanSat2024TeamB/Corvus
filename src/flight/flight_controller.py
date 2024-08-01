import asyncio
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
from pathlib import Path

from control.position_manager import PositionManager
from control.coordinates import Coordinates
#from sensor.camera_handler import CameraHandler

class FlightController:

    def __init__(self, drone: System, position_manager: PositionManager):
        self.drone: System = drone
        self.position_manager: PositionManager = position_manager
        #self.camera_handler = CameraHandler(model_path=Path(__file__).parent.parent.parent.joinpath("assets/model/cone.pt"))
        self.target_latitude = 0
        self.target_longitude = 0
        self.target_altitude = 0
        self.pos = [0,0]
        
        self.is_in_air: bool = False
        
    async def takeoff(self, takeoff_altitude) -> bool:
        await self.drone.action.set_takeoff_altitude(takeoff_altitude+2)
        await self.drone.action.takeoff()
        while self.position_manager.adjusted_altitude() <= takeoff_altitude:
            await asyncio.sleep(0.1)
        return True

    async def hovering(self, time: float) -> bool:
        await self.drone.action.hold()
        await asyncio.sleep(time)
        return True
    
    async def stop_here(self):
        await self.drone.action.hold()
    
    async def land(self) -> bool:
        await self.drone.action.land()
        return True
    
    async def disarm(self) -> bool:
        await self.drone.action.disarm()
        return True
    
    async def kill(self) -> bool:
        await self.drone.action.kill()
        return True
    
    ############################################################################################
    async def go_to(self, speed, *target_coordinates: Coordinates) -> bool:
        mission_items = []
        await self.drone.mission.clear_mission()
        print('mission cleared')
        for coordinates in target_coordinates:
            mission_items.append(MissionItem(coordinates.latitude(), coordinates.longitude(), coordinates.altitude(), speed, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
            #mission_items.append(MissionItem(coordinates.latitude(), coordinates.longitude(), coordinates.altitude(), speed, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
        mission_plan = MissionPlan(mission_items)
        print('mission plan made')
        print('do not return setting')
        await self.drone.mission.set_return_to_launch_after_mission(False)
        print('do not return start upload')
        await self.drone.mission.upload_mission(mission_plan)
        print('mission plan uploaded start mission')
        await self.drone.mission.start_mission()
        return True
    
    #async def execute_mission(self, mission_plan: MissionPlan) -> bool:
        print('do not return setting')
        await self.drone.mission.set_return_to_launch_after_mission(False)
        print('do not return start upload')
        await self.drone.mission.upload_mission(mission_plan)
        print('mission plan uploaded start mission')
        await self.drone.mission.start_mission()
        return True
    
    async def if_mission_finished(self) -> bool:
        return await self.drone.mission.is_mission_finished()

    ###################################################################################################
    async def go_to_location(self, speed, yaw_deg, target_coordinates: Coordinates):
        self.target_latitude = target_coordinates.latitude()
        self.target_longitude = target_coordinates.longitude()
        self.target_altitude = target_coordinates.altitude()
        print('target got')
        await self.drone.action.goto_location(self.target_latitude, self.target_longitude, self.target_altitude, yaw_deg)
        print('goto started')
        await self.drone.action.set_current_speed(speed)
        
        while not self.if_goto_location_finished(self.target_latitude, self.target_longitude, self.target_altitude):
            await asyncio.sleep(0.01)

    def if_goto_location_finished(self, target_latitude, target_longitude, target_altitude):
        return abs(target_altitude - self.position_manager.adjusted_altitude()) <= 1.0 and \
            abs(target_latitude - self.position_manager.adjusted_coordinates_lat()) <= 1.0e-5 and \
            abs(target_longitude - self.position_manager.adjusted_coordinates_lon()) <= 1.0e-5 ## アメリカ違う

    #########################################################################################################

    async def precise_land(self):
        while True:
            self.pos = self.camera_handler.capture_cone_position(0.5)
            print(self.pos)
            if self.pos == [None, None]:
                await asyncio.sleep(1)
            else:
                await self.stop_here()
                


    #########################################################################################################
    

    
    def update_is_in_air(self, is_in_air: bool) -> None:
        self.is_in_air = is_in_air
        return
    
    async def invoke_loop(self) -> None:
        async for is_in_air in self.drone.telemetry.in_air():
            self.update_is_in_air(is_in_air)
            await asyncio.sleep(1)