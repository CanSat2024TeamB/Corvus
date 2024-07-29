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
        self.rst = 7
        self.CRLF = "\r\n"

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
        await self.lora_write("start")

        self.is_on = True

    async def lora_write(self, message: str) -> None:
        """write lora

        Args:
            message (str): command or message to send
        """
        msg_send = str(message) + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        print('sent')
        await asyncio.sleep(4)
