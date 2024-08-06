import asyncio
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
from pathlib import Path
import math

from control.position_manager import PositionManager
from control.coordinates import Coordinates
#from sensor.camera_handler import CameraHandler, ConeDetector

class FlightController:

    def __init__(self, drone: System, position_manager: PositionManager):
        self.drone: System = drone
        self.position_manager: PositionManager = position_manager
        #self.camera_handler = CameraHandler()
        #self.cone_detector = ConeDetector(self.camera_handler)
        self.target_latitude = 0
        self.target_longitude = 0
        self.target_altitude = 0
        self.ASML = 0
        self.yaw_deg = 0
        self.detected_pos = [None,None]
        
        self.detected_flag = False
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
        print('mission plan uploading.move to hold mode')
        await self.stop_here() #####先輩のをみるとholdに入れてる
        await asyncio.sleep(10) #####アップロードにかかる時間？
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
        await self.drone.mission.start_mission()
        return True
    
    async def if_mission_finished(self) -> bool:
        return await self.drone.mission.is_mission_finished()

    ###################################################################################################
    async def go_to_location(self, speed, target_coordinates: Coordinates):
        self.target_latitude = target_coordinates.latitude()
        self.target_longitude = target_coordinates.longitude()
        self.target_altitude = target_coordinates.altitude()
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()
        
        print('target got')
        await self.drone.action.goto_location(self.target_latitude, self.target_longitude, self.AMSL+self.target_altitude, 0)
        print('goto started')
        await self.drone.action.set_current_speed(speed)
        
        while not self.if_goto_location_finished(self.target_latitude, self.target_longitude, self.target_altitude):
            await asyncio.sleep(3)
            current_alt = self.position_manager.adjusted_altitude()
            if current_alt < 1.5:
                await self.go_to_location(Coordinates(self.target_longitude,
                                                    self.target_latitude,
                                                    self.target_altitude + 2))
            elif current_alt > 10:
                await self.go_to_location(Coordinates(self.target_longitude,
                                                    self.target_latitude,
                                                    self.target_altitude - 4))
        return

    def if_goto_location_finished(self, target_latitude, target_longitude, target_altitude):
        return abs(target_altitude - self.position_manager.adjusted_altitude()) <= 1.0 and \
            abs(target_latitude - self.position_manager.adjusted_coordinates_lat()) <= 1.0e-5 and \
            abs(target_longitude - self.position_manager.adjusted_coordinates_lon()) <= 1.0e-5 ## アメリカ違う
    
    #########################################################################################################

    async def rotate_yaw(self, yaw):
        await self.drone.action.set_current_speed(0.1)
        self.target_latitude = self.position_manager.adjusted_coordinates_lat()
        self.target_longitude = self.position_manager.adjusted_coordinates_lon()
        self.target_altitude = self.position_manager.adjusted_altitude()
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()
        self.yaw_deg = yaw
        
        print('rotate')
        await self.drone.action.goto_location(self.target_latitude, self.target_longitude, self.AMSL+self.target_altitude, self.yaw_deg)

    async def decend(self,descend_m):
        await self.drone.action.set_current_speed(0.1)
        self.target_latitude = self.position_manager.adjusted_coordinates_lat()
        self.target_longitude = self.position_manager.adjusted_coordinates_lon()
        self.target_altitude = self.position_manager.adjusted_altitude()
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()

        print('descend')
        await self.drone.action.goto_location(self.target_latitude, self.target_longitude, self.AMSL+self.target_altitude-descend_m, self.yaw_deg)



    async def precise_land(self):
        while self.detected_pos == [None,None]:
            for yaw_angle in range(0, 360, 30):
                await self.go_to_location(yaw_angle)
                await asyncio.sleep(3)
                await self.stop_here()
                self.detected_pos = self.cone_detector.capture_cone_position()
                print(self.pos)
        
    

                


    #########################################################################################################

    async def fly_orbit(self, radius, velocity, yaw, latitude, longitude, altitude):
        await self.drone.action.do_orbit(radius_m=radius,
                                   velocity_ms=velocity,
                                   yaw_behavior=yaw,
                                   latitude_deg=latitude,
                                   longitude_deg=longitude,
                                   absolute_altitude_m=altitude)

    
    def update_is_in_air(self, is_in_air: bool) -> None:
        self.is_in_air = is_in_air
        return
    
    async def invoke_loop(self) -> None:
        async for is_in_air in self.drone.telemetry.in_air():
            self.update_is_in_air(is_in_air)
            await asyncio.sleep(1)