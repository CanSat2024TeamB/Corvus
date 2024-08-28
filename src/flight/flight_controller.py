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
from logger.logger import Logger

class FlightController:

    def __init__(self, drone: System, position_manager: PositionManager, logger: Logger):
        self.drone: System = drone
        self.position_manager: PositionManager = position_manager
        self.logger = logger
        self.camera_handler: CameraHandler = CameraHandler.get_instance()
        self.cone_detector: ConeDetector = ConeDetector(self.camera_handler)
        self.target_latitude = 0
        self.target_longitude = 0
        self.target_altitude = 0
        self.ASML = 0
        self.current_lidar_alt = 0
        self.yaw_deg = 0
        self.detected_pos = [None,None]
        self.nondetected_counter = 0
        self.nondetected_counter_max = 10
        self.alp = 45 ## カメラ取り付け角
        self.theta = [54, 41] ##カメラ視野角
        self.lat_unit = 110945.467 #m 緯度一度の長さ　八千代
        self.lon_unit = 90428.693 #m　経度一度の長さ　八千代

        
        self.detected_flag = False
        self.is_in_air: bool = False
        
    async def takeoff(self, takeoff_altitude) -> bool:
        take_off_max_time = 0
        await self.drone.action.set_takeoff_altitude(takeoff_altitude*2)
        await self.drone.action.takeoff()
        while self.position_manager.adjusted_altitude() <= takeoff_altitude:
            await asyncio.sleep(0.1)
            take_off_max_time += 0.1
            if take_off_max_time > 20:
                print('take off max time')
                break
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
        self.logger.write('mission cleared')

        for coordinates in target_coordinates:
            mission_items.append(MissionItem(coordinates.latitude(), coordinates.longitude(), coordinates.altitude(), speed, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
            #mission_items.append(MissionItem(coordinates.latitude(), coordinates.longitude(), coordinates.altitude(), speed, True, float('nan'), float('nan'), MissionItem.CameraAction.NONE, float('nan'), float('nan'), float('nan'), float('nan'), float('nan'), MissionItem.VehicleAction.NONE))
        mission_plan = MissionPlan(mission_items)

        print('mission plan made')
        self.logger.write('mission plan made')
        print('do not return setting')
        self.logger.write('do not return setting')

        await self.drone.mission.set_return_to_launch_after_mission(False)

        print('do not return start upload')
        self.logger.write('do not return start upload')

        await self.drone.mission.upload_mission(mission_plan)

        print('mission plan uploading.move to hold mode')
        self.logger.write('mission plan uploading.move to hold mode')

        await self.stop_here() #####先輩のをみるとholdに入れてる
        await asyncio.sleep(10) #####アップロードにかかる時間？

        print("Waiting for drone to be armable...")
        self.logger.write("Waiting for drone to be armable...")

        async for is_armable in self.drone.telemetry.health():
            if is_armable:
                print("Drone is armable")
                self.logger.write("Drone is armable")

                break
            await asyncio.sleep(0.11)

        print("Arming the drone...")
        self.logger.write("Arming the drone...")

        await self.drone.action.arm()

        async for is_armed in self.drone.telemetry.armed():
            if is_armed:
                print("drone is armed")
                self.logger.write("drone is armed")

                break
            await asyncio.sleep(0.1)
        await self.drone.mission.start_mission()
        return True
    
    async def if_mission_finished(self) -> bool:
        return await self.drone.mission.is_mission_finished()

    ###################################################################################################
    async def go_to_location(self, speed, target_coordinates: Coordinates ,circle_radious):
        self.target_latitude = target_coordinates.latitude()
        self.target_longitude = target_coordinates.longitude()
        #self.target_altitude = target_coordinates.altitude()
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()
        self.current_lidar_alt = self.position_manager.adjusted_altitude()
        
        print('current AMSL',self.AMSL)
        print('current lidar',self.current_lidar_alt)
        
        print('target got')
        self.target_final_altitude = self.AMSL
        await self.drone.action.goto_location(self.target_latitude, self.target_longitude, self.target_final_altitude, self.calculate_yaw_angle())
        print('goto started')
        await self.drone.action.set_current_speed(speed)
        
        while not self.if_goto_location_finished(self.target_latitude, self.target_longitude, circle_radious):
            await asyncio.sleep(1)
            self.current_lidar_alt = self.position_manager.adjusted_altitude()
            
            if self.current_lidar_alt < 3:
                print('altitude too low')
                self.target_final_altitude += 0.1
                print('target AMSL alt',self.target_final_altitude)
                await self.drone.action.goto_location(self.target_latitude, self.target_longitude,  self.target_final_altitude, self.calculate_yaw_angle())
                
            elif self.current_lidar_alt > 8:
                print('altitude too high')
                self.target_final_altitude -= 0.1
                print('target AMSL alt',self.target_final_altitude)
                await self.drone.action.goto_location(self.target_latitude, self.target_longitude, self.target_final_altitude, self.calculate_yaw_angle())

        await self.drone.action.set_current_speed(0.001)
        return
    
    def if_goto_location_finished(self, target_latitude, target_longitude, circle_radious):
            lat_dif = abs(target_latitude - self.position_manager.adjusted_coordinates_lat()) *  self.lat_unit 
            lon_dif = abs(target_longitude - self.position_manager.adjusted_coordinates_lon()) * self.lon_unit
            return lat_dif**2 + lon_dif**2 < circle_radious**2
    
    def calculate_yaw_angle(self):
            lat_dist = (self.target_latitude - self.position_manager.adjusted_coordinates_lat()) *  self.lat_unit
            lon_dist = (self.target_longitude - self.position_manager.adjusted_coordinates_lon()) * self.lon_unit
            yaw_deg =  90.0 - math.degrees(math.atan2(lon_dist, lat_dist))
            print(yaw_deg)
            return yaw_deg

##############################################################################################################

    async def precise_land_slope(self) -> bool:
        if not self.camera_handler.is_connected():
            await self.go_to_location(1.0, Coordinates(self.target_longitude,self.target_latitude,self.target_altitude), 1.0)
            await self.land()
            raise RuntimeError("Camera is not connected. Stopped the precies land sequence.")
     
        while self.detected_pos == [None,None]:
                await asyncio.sleep(1)
                self.detected_pos = self.cone_detector.capture_cone_position_and_save(str(Path(__file__).parent.parent.parent.joinpath(f"assets/log/img_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jpg")), 0.3)
                #self.detected_pos = self.cone_detector.get_pos(use_color_assist = True)
                print(self.detected_pos)
                self.nondetected_counter += 1
                if self.nondetected_counter == self.nondetected_counter_max:
                    await self.go_to_location(1.0, Coordinates(self.target_longitude,self.target_latitude,self.target_altitude), 0.5)
                    await self.land()
                    return 
        
        self.nondetected_counter = 0
        cone_x = self.detected_pos[0]
        cone_y = self.detected_pos[1]
        beta =  self.theta[0] * cone_x * 0.5
        gamma = self.theta[1] * cone_y * 0.5
        delta = self.calculate_delta_angle(self.target_latitude,self.target_longitude)
        print('delta') 
        self.current_lidar_alt = self.position_manager.adjusted_altitude()
        east_len_m = self.current_lidar_alt * math.tan(math.radians(self.alp + gamma)) * math.cos(math.radians(delta - beta))
        print('east_len_m')
        north_len_m = self.current_lidar_alt * math.tan(math.radians(self.alp + gamma)) * math.sin(math.radians(delta - beta))
        print('north_len_m')
        error_lon = east_len_m / self.lon_unit
        error_lat = north_len_m / self.lat_unit
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()

        await self.drone.action.goto_location(self.target_latitude + error_lat,
                                              self.target_longitude + error_lon, 
                                              self.AMSL-self.current_lidar_alt, self.calculate_yaw_angle())
        await self.drone.action.set_current_speed(0.5)
        print('last descending')

        while self.position_manager.adjusted_altitude() > 0.25:
            print('still')
            await asyncio.sleep(0.2)
        await self.land()

        return

    async def precise_land_right_angle(self) -> bool:
        if not self.camera_handler.is_connected():
            await self.go_to_location(1.0, Coordinates(self.target_longitude,self.target_latitude,self.target_altitude), 0.5)
            await self.land()
            raise RuntimeError("Camera is not connected. Stopped the precies land sequence.")
     
        while self.detected_pos == [None,None]:
                await asyncio.sleep(1)
                self.detected_pos = self.cone_detector.capture_cone_position_and_save(str(Path(__file__).parent.parent.parent.joinpath(f"assets/log/img_{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}.jpg")), 0.3)
                print(self.detected_pos)
                #self.detected_pos = self.cone_detector.get_pos(use_color_assist = True)
                #print(self.detected_pos)
                self.nondetected_counter += 1
                if self.nondetected_counter == self.nondetected_counter_max:
                    await self.go_to_location(1.0, Coordinates(self.target_longitude,self.target_latitude,self.target_altitude), 0.5)
                    await self.land()
                    return 
        
        self.nondetected_counter = 0
        cone_x = self.detected_pos[0]
        cone_y = self.detected_pos[1]
        beta =  self.theta[0] * cone_x * 0.5
        gamma = self.theta[1] * cone_y * 0.5
        delta = self.calculate_delta_angle(self.target_latitude,self.target_longitude) 
        print('delta') 
        self.current_lidar_alt = self.position_manager.adjusted_altitude()
        east_len_m = self.current_lidar_alt * math.tan(math.radians(self.alp + gamma)) * math.cos(math.radians(delta - beta))
        print('east_len_m')
        north_len_m = self.current_lidar_alt * math.tan(math.radians(self.alp + gamma)) * math.sin(math.radians(delta - beta))
        print('north_len_m')
        error_lon = east_len_m / self.lon_unit
        error_lat = north_len_m / self.lat_unit
        self.AMSL = self.position_manager.adjusted_coordinates_AMSL()

        await self.go_to_location(0.5, Coordinates(self.target_latitude + error_lat, self.target_longitude + error_lon, self.AMSL), 0.5)
        await self.land()

        return 
        

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
        DECENDING_SPEED = 0.5 #降下速度（2^0.5を乗じた値が降下速度）
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

        def calc_velocity_body_to_target(self) -> VelocityBodyYawspeed:
            #yaw_rad = yaw_deg * math.pi / 180
            #return VelocityBodyYawspeed(math.cos(yaw_rad), math.sin(yaw_rad), 1.0, 0.0)
            return VelocityBodyYawspeed(1.0, 0.0, 1.0, 0.0)
        
        async def rotate_and_search_cone(self, rotate_rate: float) -> bool:
            search_time = 60 #この秒数見つからなかったら強制的に着陸
            await turn_clock_wise(self, rotate_rate)
            
            time_start = time.perf_counter()
            while True: ####### コーンがみつからなかったときに近くを徘徊するコードがまだない
                # await set_altitude(3)
                pos = self.cone_detector.get_pos(use_color_assist = True)

                if pos[0] is not None:
                    print("cone detected")
                    print(f"cone pos: {pos}")
                    await stop_rotation(self)
                    await asyncio.sleep(1)

                    return True ## 一旦２回チェックしないようにした

                    pos = self.cone_detector.get_pos(use_color_assist = True)
                    if pos[0] is not None:
                        print("cone position confirmed")
                        print(f"confirmed cone pos: {pos}")
                        return True
                    else:
                        return await rotate_and_search_cone(self, rotate_rate / 2) # コーンを認識して止まった後、静止状態でもう一回とって認識できなかったらゆっくり回ってもう一回（推定のラグを考慮）

                time_now = time.perf_counter()
                if time_now - time_start > search_time:
                    return False
                
        async def approach_cone(self):
            found_cone = await rotate_and_search_cone(self, 10)
            if found_cone:
                nonlocal CAMERA_YAW_DEG
                nonlocal LAND_ALTITUDE
                nonlocal DECENDING_SPEED

                await set_velocity_body(self, multiply_velocity_body(calc_velocity_body_to_target(self), DECENDING_SPEED))

                while True:
                    pos = self.cone_detector.get_pos(use_color_assist = True)
                    if pos[0] is not None:
                        print("cone detected while approaching cone")
                        print(f"pos: {pos}")
                        await adjust_velocity(self, CAMERA_YAW_DEG, pos)
                    else:
                        print("lost cone")
                        await set_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                        print("restarting searching cone")
                        return await approach_cone(self)
                    
                    if self.position_manager.adjusted_altitude() < LAND_ALTITUDE:
                        print("got ready to land")
                        # await set_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                        return
            else:
                print("Could not find cone in the searching process.")
                # await set_velocity_body(self, VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
                return

        print("start precise landing")

        await set_position(self, position)
        await set_velocity_body(self, velocity_body)
        
        print("starting offboard landing...")
        try:
            await self.drone.offboard.start()
            #print("setting altitude 3 m")
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