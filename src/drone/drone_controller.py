import asyncio
from mavsdk import System

from sensor.lidar_handler import LiDARHandler
from control.coordinates import Coordinates
from control.battery import Battery_watch
from control.gps_handler import GPSHandler
from control.position_manager import PositionManager
from control.compass_handler import CompassHandler
from flight.flight_controller import FlightController
from logger.logger import Logger
from sensor.acceleration_velocity import Acceleration_Velocity
from sensor.camera_handler import CameraHandler
from lora.lora import Lora


class DroneController:
    pixhawk_address: str = "serial:///dev/ttyACM0:115200"
    #pixhawk_address: str = "udp://:14540"

    default_log_dir = "/home/admin/corvus/assets/log"

    def __init__(self, log_dir = default_log_dir):
        self.drone_instance = System()
        #self.drone = System(mavsdk_server_address='localhost', port=50051)
        self.lidar_handler = LiDARHandler(self.drone_instance)
        self.gps_handler = GPSHandler(self.drone_instance)
        self.battery_watch = Battery_watch(self.drone_instance)
        self.compass_handler = CompassHandler(self.drone_instance)
        self.position_manager = PositionManager(self.drone_instance, self.gps_handler, self.compass_handler, self.lidar_handler)
        self.logger = Logger(log_dir)
        self.flight_controller = FlightController(self.drone_instance, self.position_manager, self.logger)
        self.ac_vel = Acceleration_Velocity(self.drone_instance)
        self.lora = Lora(self.drone_instance)

        self.tasks = []
       

    def get_drone_instance(self):
        return self.drone_instance
    
    def get_position_manager_instance(self):
        return self.position_manager

    def get_logger_instance(self):
        return self.logger
    
    def get_lora_instance(self):
        return self.lora

    async def connect(self) -> bool:
        print("Connecting...")
        self.logger.write('Connecting...')
        await self.drone_instance.connect(system_address = self.pixhawk_address)
        print("Waiting for drone to connect...")
        self.logger.write("Waiting for drone to connect...")

        async for state in self.drone_instance.core.connection_state():
            if state.is_connected:
                print(f"Connected to drone!")
                self.logger.write("Connected to drone!")
                break
            await asyncio.sleep(0.1)

    async def gps_ok(self):
        async for health in self.drone_instance.telemetry.health():
                if health.is_global_position_ok and health.is_home_position_ok:
                    self.logger.write("Global position estimate OK")
                    break

        return True
    
    
    async def arm(self) -> bool:
        print('gps check start')
        await self.gps_handler.catch_gps()
        print('global and local position ok')      
        self.logger.write('global and local position ok')

        print("Waiting for drone to be armable...")
        self.logger.write("Waiting for drone to be armable...")
        async for is_armable in self.drone_instance.telemetry.health():
            if is_armable:
                print("Drone is armable")
                self.logger.write("Drone is armable")
                break
            await asyncio.sleep(0.11)

        print("Arming the drone...")
        self.logger.write("Arming the drone...")
        await self.drone_instance.action.arm()

        async for is_armed in self.drone_instance.telemetry.armed():
            if is_armed:
                print("drone is armed")
                self.logger.write("drone is armed")
                break
            await asyncio.sleep(0.1)
        
        return True
    
    async def logger_write(self):
        while True:
            await asyncio.sleep(1)
            message_1 = str(self.position_manager.adjusted_altitude())
            message_2 = str(self.position_manager.adjusted_coordinates_lon())
            message_3 = str(self.position_manager.adjusted_coordinates_lat())
            #message_4 = str(self.ac_vel.get_velocity())
            #message_5 = str(self.battery_watch.remaining_percent())
            #message_6 = str(self.battery_watch.voltage_v())
            #message_7 = str(self.battery_watch.temperature_degc())
            
            self.logger.write(message_1,message_2,message_3)

    async def lora_write(self):
        while True:
            #message_4 = str(self.position_manager.adjusted_altitude())
            message_5 = str(round(self.position_manager.adjusted_coordinates_lon(), 4))
            message_6 = str(round(self.position_manager.adjusted_coordinates_lat(), 4))

            #message_4 = str(self.ac_vel.get_velocity())
            #message_5 = str(self.battery_watch.remaining_percent())
            #message_6 = str(self.battery_watch.voltage_v())
            #message_7 = str(self.battery_watch.temperature_degc())
            
            message = ' '.join([message_6, message_5])
            await self.lora.lora_send(message)
            await asyncio.sleep(30)
    
    async def lidar_test(self):
        while True:
            print(self.position_manager.adjusted_altitude())
            await asyncio.sleep(0.5)

#############################################################################################
    async def invoke_sensor(self) -> None:
        # すべてのタスクをリストに追加
        self.tasks.extend([
            asyncio.create_task(self.lidar_handler.invoke_loop()),
            asyncio.create_task(self.gps_handler.invoke_loop()),
            # asyncio.create_task(self.battery_watch.invoke_loop()),  # バッテリーハンドラのコルーチンが必要なら追加
            asyncio.create_task(self.compass_handler.invoke_loop()),
            # asyncio.create_task(self.flight_controller.invoke_loop()),  # フライトコントローラのコルーチンが必要なら追加
            asyncio.create_task(self.logger_write()),
            asyncio.create_task(self.lora_write())
        ])

        # 全てのタスクが完了するのを待つ
        await asyncio.sleep(float('inf'))

    async def lidar_test_loop(self) -> None:
        # すべてのタスクをリストに追加
        self.tasks.extend([
            asyncio.create_task(self.lidar_handler.invoke_loop()),
            asyncio.create_task(self.compass_handler.invoke_loop()),
            asyncio.create_task(self.lidar_test())
        ])

        # 全てのタスクが完了するのを待つ
        await asyncio.sleep(float('inf'))

    async def camera_calc_test_loop1(self) -> None:
        # すべてのタスクをリストに追加
        self.tasks.extend([
            asyncio.create_task(self.lidar_handler.invoke_loop()),
            asyncio.create_task(self.compass_handler.invoke_loop())
        ])

        # 全てのタスクが完了するのを待つ
        await asyncio.sleep(float('inf'))

    async def camera_calc_test_loop2(self) -> None:
        # すべてのタスクをリストに追加
        self.tasks.extend([
            asyncio.create_task(self.lidar_handler.invoke_loop()),
            asyncio.create_task(self.compass_handler.invoke_loop()),
            asyncio.create_task(self.gps_handler.invoke_loop())
        ])

        # 全てのタスクが完了するのを待つ
        await asyncio.sleep(float('inf'))

    async def add_sequence_task(self, coro):
        if not hasattr(self, 'tasks'):
            self.tasks = []

        # 新しいタスクを追加
        new_task = asyncio.create_task(coro)
        self.tasks.append(new_task)
        print('added task')
    
    async def exe_sequence_task(self, coro):
        if not hasattr(self, 'tasks'):
            self.tasks = []

        # 新しいタスクを追加
        new_task = asyncio.create_task(coro)
        self.tasks.append(new_task)
        print('added task')

        for task in self.tasks:
            await task
        
####################################################################################################
    
    async def sequence_test_hovering(self):
        await self.flight_controller.takeoff(3)
        print('reached start hovering')
        self.logger.write('reached start hovering')
        await self.flight_controller.hovering(10)
        print('finish hovering start landing')
        self.logger.write('finish hovering start landing')
        await self.flight_controller.land()

    async def sequence_test_mission(self,speed, *target_coordinates: Coordinates):
        await self.flight_controller.go_to(speed, *target_coordinates)
        print('mission started')
        self.logger.write('mission started')
        while True:
            await asyncio.sleep(0.1)
            mission_completed = await self.flight_controller.if_mission_finished()
            if mission_completed:
                print('mission finished start hovering')
                self.logger.write('mission finished start hovering')
                await self.flight_controller.hovering(5)
                print(' hovering finished start landing')
                self.logger.write('hovering finished start landing')
                await self.flight_controller.land()
                print("landed")
                self.logger.write("landed")
                break

    async def sequence_test_goto(self,speed, target_coordinates: Coordinates):
        print("arming")
        self.logger.write("arming")
        await self.arm()
        print("taking off...")
        self.logger.write("taking off...")
        await self.flight_controller.takeoff(target_coordinates.altitude())
        print('reached')
        self.logger.write('reached')
        await self.flight_controller.hovering(5)
        print('goto started')
        self.logger.write('goto started')
        await self.flight_controller.go_to_location(speed, target_coordinates, 10.0)
        print('goto finished start hovering')
        self.logger.write('goto finished start hovering')
        await self.flight_controller.hovering(20)
        print('hovering finished start landing')
        self.logger.write('hovering finished start landing')
        await self.flight_controller.land()
        print("landed")
        self.logger.write("landed")

    async def sequence_test_endurance(self,speed, *target_coordinates: Coordinates): #要書き換え
        await self.flight_controller.takeoff(5)
        await self.flight_controller.hovering(10)
        await self.flight_controller.go_to(speed, *target_coordinates)
        while True:
            await asyncio.sleep(1)
            if self.battery_watch.remaining_percent()<35:
                await self.flight_controller.land()
######################################################################################################################    
    async def sequence_test_precise_land(self):
        print("taking off")
        await self.flight_controller.takeoff(5)
        print("finished taking off")
        await self.flight_controller.hovering(10)
        print("start landing")
        try:
            await self.flight_controller.offboard_precise_land()
        except RuntimeError as e:
            print(e)
            await self.flight_controller.land()
        print("landed")
#########################################################################################################################    
    async def sequence_test_goto_and_precise_land_slope(self, speed, target_coordinates: Coordinates):
        print("arming")
        self.logger.write("arming")
        await self.arm()
        print("taking off...")
        self.logger.write("taking off...")
        await self.flight_controller.takeoff(target_coordinates.altitude())
        print("finished taking off")
        await self.flight_controller.hovering(5)
        print('goto started')
        await self.flight_controller.go_to_location(speed, target_coordinates, 10)
        print("start precise landing")
        try:
            await self.flight_controller.precise_land_slope()
        except RuntimeError as e:
            print(e)
        print("landed")
###############################################################################################################################
    async def sequence_test_goto_and_precise_land_right_angle(self, speed, target_coordinates: Coordinates):
        print("arming")
        self.logger.write("arming")
        await self.arm()
        print("taking off...")
        self.logger.write("taking off...")
        await self.flight_controller.takeoff(target_coordinates.altitude())
        print("finished taking off")
        await self.flight_controller.hovering(5)
        print('goto started')
        await self.flight_controller.go_to_location(speed, target_coordinates, 8)
        print("start precise landing")
        try:
            await self.flight_controller.precise_land_right_angle()
        except RuntimeError as e:
            print(e)
        print("landed")

    async def sequence_test_goto_and_precise_land_right_angle_calc_test(self):
        await self.flight_controller.precise_land_right_angle_calc_confirm_test()
#####################################################################################################################################
    async def sequence_test_precise_land_vertical(self, speed, target_coordinates: Coordinates):
        print("arming")
        self.logger.write("arming")
        await self.arm()
        print("taking off...")
        self.logger.write("taking off...")
        await self.flight_controller.takeoff(target_coordinates.altitude())
        print("finished taking off")
        await self.flight_controller.hovering(5)
        print('goto started')
        await self.flight_controller.go_to_location(speed, target_coordinates, 0.5)
        print("start precise landing")
        await self.flight_controller.precise_land_vertical()
        print('end')

    async def precise_land_vertical_calc_test(self):
        await self.flight_controller.precise_land_vertical_calc_test()

#########################################################################################################################################

    async def sequence_test_precise_land_using_color(self, speed, target_coordinates: Coordinates):
        print("arming")
        self.logger.write("arming")
        await self.arm()
        print("taking off...")
        self.logger.write("taking off...")
        await self.flight_controller.takeoff(target_coordinates.altitude())
        print("finished taking off")
        await self.flight_controller.hovering(5)
        print('goto started')
        await self.flight_controller.go_to_location(speed, target_coordinates, 0.5)
        print("start precise landing")
        await self.flight_controller.offboard_land_using_color()
        print('end')
#########################################################################################################################
    async def capture_video_during_flight(self, speed, target_coordinates, output_path, video_length):
        print("arming")
        self.logger.write("arming")
        await self.arm()
        print("taking off...")
        self.logger.write("taking off...")
        await self.flight_controller.takeoff(5)
        print("finished taking off")
        await self.flight_controller.go_to_location(speed, target_coordinates, 0.5)
        camera_handler = CameraHandler.get_instance()
        if camera_handler.is_connected():
            print(f"start capturing {video_length} s video")
            camera_handler.capture_video(output_path, video_length)
        else:
            print("Camera is not connected.")
        await self.flight_controller.hovering(video_length)
        await self.flight_controller.land()

###########################################################################################################    
