import asyncio
from mavsdk import System
from mavsdk.mission import (MissionItem, MissionPlan)
from mavsdk.offboard import (Attitude, PositionNedYaw, VelocityBodyYawspeed, OffboardError)
from pathlib import Path
import math

import time
import datetime

from control.position_manager import PositionManager
from control.coordinates import Coordinates
from sensor.camera_handler import CameraHandler, ConeDetector

class FlightController:

    def __init__(self, drone: System, position_manager: PositionManager):
        self.drone: System = drone
        self.position_manager: PositionManager = position_manager
        self.camera_handler: CameraHandler = CameraHandler.get_instance()
        self.cone_detector: ConeDetector = ConeDetector(self.camera_handler)
        self.target_latitude = 0
        self.target_longitude = 0
        self.target_altitude = 0
        self.ASML = 0
        self.yaw_deg = 0
        self.detected_pos = [None,None]
        self.nondetected_counter = 0
        self.nondetected_counter_max = 10
        self.alp = 45 ## カメラ取り付け角
        self.theta = [54, 41] ##カメラ視野角
        self.lat_unit = 110964.027 #m 緯度一度の長さ　八千代
        self.lon_unit = 90424.106 #m　経度一度の長さ　八千代

        
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
            if current_alt < 2:
                print('altitude too low')
                await self.go_to_location(Coordinates(self.target_longitude, self.target_latitude, self.target_altitude + 2))
                break                                    
            elif current_alt > 8:
                print('altitude too high')
                await self.go_to_location(Coordinates(self.target_longitude, self.target_latitude, self.target_altitude - 4))
                break
        await self.stop_here()
        return

    def if_goto_location_finished(self, target_latitude, target_longitude, target_altitude):
        #return abs(target_altitude - self.position_manager.adjusted_altitude()) <= 1.0 and \
            #abs(target_latitude - self.position_manager.adjusted_coordinates_lat()) *  self.lat_unit <= 2.0 and \
            #abs(target_longitude - self.position_manager.adjusted_coordinates_lon()) * self.lon_unit <= 2.0 
    
        return abs(target_latitude - self.position_manager.adjusted_coordinates_lat()) *  self.lat_unit <= 2.0 and \
            abs(target_longitude - self.position_manager.adjusted_coordinates_lon()) * self.lon_unit <= 2.0 

##############################################################################################################

    async def precise_land(self) -> bool:
        if not self.camera_handler.is_connected():
            raise RuntimeError("Camera is not connected. Stopped the precies land sequence.")
        
        while self.detected_pos == [None,None]:
                await asyncio.sleep(1)
                self.detected_pos = self.cone_detector.capture_cone_position_and_save(str(Path(__file__).parent.parent.parent.joinpath(f"assets/log/img_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jpg")), 0.3)
                print(self.detected_pos)
                self.nondetected_counter += 1
                if self.nondetected_counter == self.nondetected_counter_max:
                    self.go_to_location(1.0, Coordinates(self.target_longitude,self.target_latitude,self.target_altitude))
                    self.land()
                    return
        
        self.nondetected_counter = 0
        cone_x = self.detected_pos[0]
        cone_y = self.detected_pos[1]
        beta =  self.theta[0] * cone_x * 0.5
        gamma = self.theta[1] * cone_y * 0.5
        delta = self.calculate_delta_angle(self.target_latitude,self.target_longitude) 
        alt = self.position_manager.adjusted_altitude()
        east_len_m = alt * math.tan(math.radians(self.alp + gamma)) * math.cos(math.radians(delta - beta))
        north_len_m = alt * math.tan(math.radians(self.alp + gamma)) * math.sin(math.radians(delta - beta))
        error_lon = east_len_m / self.lon_unit
        error_lat = north_len_m / self.lat_unit
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()

        await self.drone.action.goto_location(self.target_latitude + error_lat,
                                              self.target_longitude + error_lon, 
                                              self.AMSL, 0)
        await self.drone.action.set_current_speed(0.5)

        while self.position_manager.adjusted_altitude() > 0.25:
            await asyncio.sleep(0.2)
        self.land()

        return True
        

    def calculate_delta_angle(self,target_latitude, target_longitude):
        current_lat = self.position_manager.adjusted_coordinates_lat()
        current_lon = self.position_manager.adjusted_coordinates_lon()

        d_lat = target_latitude - current_lat
        d_lon = target_longitude - current_lon

        x = self.lon_unit * d_lon
        y = self.lat_unit * d_lat
        return math.degrees(math.atan2(x, y)) ##-180~180

    #########################################################################################################

    async def offboard_precise_land(self) -> bool:        
        CAMERA_YAW_DEG = 0 #pixhawk正面からはかったカメラの指向方向 (deg, 右回り正)
        LAND_ALTITUDE = 0.25 #コーンに接近していってlandに移行する高度
        PROB_THRESHOLD = 0.2 #画像認識probabilityの閾値
        DECENDING_SPEED = 1 #降下速度（2^0.5を乗じた値が降下速度）
        ADJUST_FACTOR = 0.1 #上下左右方向の補正係数

        print("checking camera connection...")
        if not self.camera_handler.is_connected():
            raise RuntimeError("Camera is not connected. Stopped the precies land sequence.")
        print("camaera connection checked")

        position = PositionNedYaw(0.0, 0.0, 0.0, 0.0)
        velocity_body = VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        
        async def set_position(self, new_position: PositionNedYaw):
            nonlocal position
            position = new_position
            await self.drone.offboard.set_position_ned(position)

        async def set_altitude(self, altitude: float):
            nonlocal position
            await set_position(self, PositionNedYaw(position.north_m, position.east_m, -1 * altitude, self.position_manager.yaw_deg()))
            
            alt_threshold = 0.5
            while True:
                if abs(self.position_manager.adjusted_altitude() - altitude) < alt_threshold:
                    return

        async def set_velocity_body(self, new_velocity_body: VelocityBodyYawspeed):
            nonlocal velocity_body
            velocity_body = new_velocity_body
            await self.drone.offboard.set_velocity_body(velocity_body)

        async def add_velocity_body(self, delta_velocity: VelocityBodyYawspeed):
            nonlocal velocity_body
            velocity_body = VelocityBodyYawspeed(velocity_body.forward_m_s + delta_velocity.forward_m_s, velocity_body.right_m_s + delta_velocity.right_m_s, velocity_body.down_m_s + delta_velocity.down_m_s, velocity_body.yawspeed_deg_s + delta_velocity.yawspeed_deg_s)
            await self.drone.offboard.set_velocity_body(velocity_body)

        async def turn_clock_wise(self, speed: float):
            """
            set yaw angular veocity of the drone
            Parameter
            ---------
            speed : float
                clock-wise angular speed rate (degree / s), negative param cause anti-clock-wise rotation.
            """
            await add_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, speed))

        async def stop_rotation(self):
            nonlocal velocity_body
            await set_velocity_body(self, VelocityBodyYawspeed(velocity_body.forward_m_s, velocity_body.right_m_s, velocity_body.down_m_s, 0.0))
        
        def multiply_velocity_body(velocity_body: VelocityBodyYawspeed, f: float) -> VelocityBodyYawspeed:
            return VelocityBodyYawspeed(velocity_body.forward_m_s * f, velocity_body.right_m_s * f, velocity_body.down_m_s * f, velocity_body.yawspeed_deg_s)

        async def adjust_velocity(self, yaw_deg, pos):
            nonlocal ADJUST_FACTOR
            yaw_rad = yaw_deg * math.pi / 180
            normalized_delta_velocity = VelocityBodyYawspeed(pos[0] * (-1 * math.sin(yaw_rad)), pos[0] * math.cos(yaw_rad), pos[1], 0.0)
            await add_velocity_body(self, multiply_velocity_body(normalized_delta_velocity, ADJUST_FACTOR))

        def calc_velocity_body_to_target(yaw_deg) -> VelocityBodyYawspeed:
            """
            get normalized VelocityBodyYawspeed from yaw_deg, down rate = 1 m/s
            Parameter
            ---------
            yaw_deg: float
                clock-wise deg angular of target measured from north (north -> 0, east -> 90)
            """
            yaw_rad = yaw_deg * math.pi / 180
            return VelocityBodyYawspeed(math.cos(yaw_rad), math.sin(yaw_rad), 1.0, 0.0)
        
        async def rotate_and_search_cone(self, rotate_rate: float) -> bool:
            search_time = 60 #この秒数見つからなかったら強制的に着陸
            await turn_clock_wise(self, rotate_rate)
            
            time_start = time.perf_counter()
            while True: ####### コーンがみつからなかったときに近くを徘徊するコードがまだない
                await set_altitude(3)
                pos = self.cone_detector.get_pos()

                if pos[0] >= -1:
                    await stop_rotation(self)
                    await asyncio.sleep(1)

                    pos = self.cone_detector.get_pos()
                    if pos[0] >= -1:
                        print("cone detected")
                        print(f"cone pos: {pos}")
                    else:
                        await rotate_and_search_cone(self, rotate_rate / 2) # コーンを認識して止まった後、静止状態でもう一回とって認識できなかったらゆっくり回ってもう一回（推定のラグを考慮）
                    return True

                time_now = time.perf_counter()
                if time_now - time_start > search_time:
                    return False
                
        async def approach_cone(self):
            found_cone = await rotate_and_search_cone(self, 20)
            if found_cone:
                body_yaw_deg = self.position_manager.yaw_deg()
                nonlocal CAMERA_YAW_DEG
                nonlocal LAND_ALTITUDE
                nonlocal DECENDING_SPEED

                await set_velocity_body(self, multiply_velocity_body(calc_velocity_body_to_target(body_yaw_deg + CAMERA_YAW_DEG), DECENDING_SPEED))
                while True:
                    pos = self.cone_detector.get_pos()
                    if pos[0] >= -1:
                        print("cone detected while approaching cone")
                        print(f"pos: {pos}")
                        body_yaw_deg = self.position_manager.yaw_deg()
                        await adjust_velocity(self, body_yaw_deg + CAMERA_YAW_DEG, pos)
                    else:
                        print("lost cone")
                        set_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                        print("restarting searching cone")
                        await approach_cone(self)
                        return
                    
                    if self.position_manager.adjusted_altitude() < LAND_ALTITUDE:
                        print("got ready to land")
                        set_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                        return
            else:
                print("Could not find cone in the searching process.")
                set_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                return
        
        await set_position(self, position)
        await set_velocity_body(self, velocity_body)
        
        print("starting offboard landing...")
        try:
            await self.drone.offboard.start()
            print("setting altitude 3 m")
            #await set_altitude(3)
            
            self.cone_detector.start(PROB_THRESHOLD)

            await approach_cone(self)

            await self.cone_detector.stop()
            print("stopped cone detector loop")
            await self.drone.offboard.stop()
            print("finished drone offboard control")

            await self.land()

            return True
        except OffboardError as error:
            print(f"Starting offboard controll failed, {error._result.result}")
            return False

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