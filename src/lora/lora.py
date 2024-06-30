import os
import sys
import RPi.GPIO as GPIO
import serial
import time
import asyncio
import struct


sys.path.append(os.getcwd())



class Lora:
    def __init__(self,drone):
        self.drone = drone
        # pin number
        # reset
        self.rst = 17
        # Vin
        self.power = 4

        # 改行文字
        self.CRLF = "\r\n"
        # massage received from PC on ground
        self.msg_received = "hello, world"

        # serial
        self.serial = serial.Serial("/dev/ttyS0", 19200, timeout=1)

        # power
        self.is_on = False
        
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)
        GPIO.setup(self.power, GPIO.OUT)

    async def power_off(self) -> None:
        """cut power for lora"""
        GPIO.output(self.power, GPIO.LOW)
        self.is_on = False
        await asyncio.sleep(1)

    async def power_on(self):
        """start lora"""
        GPIO.output(self.power, GPIO.HIGH)

        GPIO.output(self.rst, GPIO.LOW)
        await asyncio.sleep(2)
        GPIO.output(self.rst, GPIO.HIGH)
        await asyncio.sleep(2)
        print("lora power on")
        #await self.write("processor")
        await self.write("start")

        self.is_on = True

    async def write(self, message: str) -> None:
        """write lora

        Args:
          massage (str): command or massage to send
        """
        #         self.is_sending = True
        msg_send = str(message) + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        await asyncio.sleep(4)

    #         self.is_sending = False

    async def read(self) -> None:
        """clear header and read lora"""
        data = self.serial.readline()
        fmt = "4s4s4s" + str(len(data) - 14) + "sxx"  # rssi, rcvidが両方onの時のヘッダー除去

        try:
            line = struct.unpack(fmt, data)
            self.msg_received = line[3].decode("ascii")
            await asyncio.sleep(1)
        except struct.error:
            await asyncio.sleep(1)
