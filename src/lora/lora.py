#import os
#import sys
import RPi.GPIO as GPIO
import serial
import asyncio
import struct


#sys.path.append(os.getcwd())



class Lora:
    def __init__(self, drone):
        self.drone = drone
        self.rst = 18
        self.CRLF = "\r\n"
        self.msg_received = "hello, world"

        try:
            self.serial = serial.Serial("/dev/serial0", 19200, timeout=None)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise e

        self.is_on = False
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)

    async def change_mode(self):
        """start lora"""
        GPIO.output(self.rst, GPIO.LOW)
        await asyncio.sleep(2)
        GPIO.output(self.rst, GPIO.HIGH)
        await asyncio.sleep(2)
        print("lora power on")
        await self.write("start")

        self.is_on = True

    async def write(self, message: str) -> None:
        """write lora

        Args:
            message (str): command or message to send
        """
        msg_send = str(message) + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        print('sent')
        await asyncio.sleep(4)

    async def read(self) -> None:
        """clear header and read lora"""
        print('read start')
        data = self.serial.readline()
        fmt = "4s4s4s" + str(len(data) - 14) + "sxx"  # rssi, rcvidが両方onの時のヘッダー除去

        try:
            line = struct.unpack(fmt, data)
            self.msg_received = line[3].decode("ascii")
            await asyncio.sleep(1)
        except struct.error as e:
            print(f"Error unpacking data: {e}")
            await asyncio.sleep(1)
