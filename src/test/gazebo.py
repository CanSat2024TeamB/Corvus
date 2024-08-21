import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import asyncio
from mavsdk import System
from mavsdk.camera import Mode, CameraError
from mavsdk.offboard import VelocityBodyYawspeed, PositionNedYaw
from threading import Thread
from socket import socket
from socket import AF_INET, SOCK_DGRAM
import cv2
import time

from drone.gazebo_drone_controller import GazeboDroneController
from control.coordinates import Coordinates

async def run():
    drone: GazeboDroneController = GazeboDroneController()

    await drone.connect()

    asyncio.create_task(drone.invoke_sensor())

    await drone.arm()
    await drone.flight_controller.takeoff(5)
    await drone.flight_controller.hovering(5)
    await drone.flight_controller.go_to_location(8, Coordinates(139.986, 40.14324473, 5))
    print("reached target point")
    await drone.flight_controller.land()

async def test_lidar():
    drone: GazeboDroneController = GazeboDroneController()
    await drone.connect()

    async for distance_sensor in drone.get_drone_instance().telemetry.distance_sensor():
        max_dinstance = distance_sensor.maximum_distance_m
        min_distance = distance_sensor.minimum_distance_m
        lidar = distance_sensor.current_distance_m
        print("max:", max_dinstance, "min:", min_distance, "now:", lidar)

async def test_gps():
    drone: GazeboDroneController = GazeboDroneController()
    await drone.connect()

    async for data in drone.get_drone_instance().telemetry.raw_gps():
        print(data)

async def test_camera():
    def udp_receive():
        src_ip = "127.0.0.1"
        src_port = 5600
        src_adress = (src_ip, src_port)

        BUFSIZE = 1024
        udp_server_socket = socket(AF_INET, SOCK_DGRAM)
        udp_server_socket.bind(src_adress)

        while True:
            data, address = udp_server_socket.recvfrom(BUFSIZE)
            print(len(data))

    def capture():
        video = cv2.VideoCapture("udpsrc port=5600 ! application/x-rtp,payload=96,encoding-name=H264 ! rtpjitterbuffer mode=1 ! rtph264depay ! h264parse ! decodebin ! videoconvert ! appsink", cv2.CAP_GSTREAMER)
        
        while True:
            print(f"is camera connected: {video.isOpened()}")
            time.sleep(0.1)
            
    drone: GazeboDroneController = GazeboDroneController()
    await drone.connect()
    asyncio.create_task(drone.invoke_sensor())
    await drone.arm()
    await drone.flight_controller.takeoff(5)

    print("finish taking off")

    capture_thread = Thread(target=capture, daemon=True)
    capture_thread.start()

    await asyncio.sleep(5)
    await drone.flight_controller.land()

async def test_offboard():
    drone: GazeboDroneController = GazeboDroneController()
    await drone.connect()

    asyncio.create_task(drone.invoke_sensor())

    await drone.arm()
    await drone.flight_controller.takeoff(5)
    await drone.flight_controller.hovering(3)

    print("start offboard mode")

    await drone.get_drone_instance().offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    await drone.get_drone_instance().offboard.set_velocity_body(VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0))
    print("starting")
    await drone.get_drone_instance().offboard.start()

    print("-- acsending 3 m")
    await drone.get_drone_instance().offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -3.0, 0.0))
    await asyncio.sleep(5)

    print("north 5 m")
    await drone.get_drone_instance().offboard.set_position_ned(PositionNedYaw(5.0, 0.0, -3.0, 0.0))
    await asyncio.sleep(5)

    print("stopping offboard")
    await drone.get_drone_instance().offboard.stop()

if __name__ == "__main__":
    asyncio.run(test_offboard())