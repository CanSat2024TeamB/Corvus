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
            self.serial = serial.Serial("/dev/ttyAMA", 9600, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise e

        self.is_on = False
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)


    async def lora_reset(self):
        """start lora"""
        GPIO.output(self.rst, GPIO.LOW)
        await asyncio.sleep(2)
        GPIO.output(self.rst, GPIO.HIGH)
        await asyncio.sleep(2)
        print("lora power on")
        await self.lora_write("start")

        self.is_on = True

    async def lora_set_sync(self, sync_num):
        self.serial_write(f'p2p set_sync {sync_num}')

    async def lora_set_freq(self,freq_num):
        self.serial_write(f'p2p set_freq {freq_num}')

    async def lora_set_sf(self,sf_num):
        self.serial_write(f'p2p set_sf {sf_num}')

    async def lora_set_bw(self,bw_num):
        self.serial_write(f'p2p set_bw {bw_num}')

    async def lora_save(self):
        self.serial_write(f'p2p save')

    async def lora_write(self,message:str):
        self.serial_write(f'p2p tx {message}')



    async def serial_write(self, message: str) -> None:
        msg_send = str(message) + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        print('sent')
        await asyncio.sleep(4)

    def lora_end(self):
        GPIO.cleanup()
