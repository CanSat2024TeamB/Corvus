#import os
#import sys
import RPi.GPIO as GPIO
import serial
import asyncio

class Lora:
    def __init__(self, drone):
        self.drone = drone
        self.rst = 7
        self.CRLF = "\r\n"

        try:
            self.serial = serial.Serial("/dev/ttyAMA0", 9600, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise e

        self.is_on = False
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)

    async def lora_reset(self):
        """Start Lora"""
        GPIO.output(self.rst, GPIO.LOW)
        await asyncio.sleep(2)
        GPIO.output(self.rst, GPIO.HIGH)
        await asyncio.sleep(2)
        print("Lora power on")
        await self.lora_write("start")
        self.is_on = True

    async def lora_set_sync(self, sync_num):
        await self.serial_write(f'p2p set_sync {sync_num}')
        response = await self.serial_read()
        print('Received:', response)

    async def lora_set_freq(self, freq_num):
        await self.serial_write(f'p2p set_freq {freq_num}')
        response = await self.serial_read()
        print('Received:', response)

    async def lora_set_sf(self, sf_num):
        await self.serial_write(f'p2p set_sf {sf_num}')
        response = await self.serial_read()
        print('Received:', response)

    async def lora_set_bw(self, bw_num):
        await self.serial_write(f'p2p set_bw {bw_num}')
        response = await self.serial_read()
        print('Received:', response)

    async def lora_save(self):
        await self.serial_write('p2p save')
        response = await self.serial_read()
        print('Received:', response)

    async def lora_write(self, message: str):
        await self.serial_write(f'p2p tx {message}')
        response = await self.serial_read()
        print('Received:', response)

    async def serial_write(self, message: str) -> None:
        msg_send = self.str_to_hex(message) + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        print('Sent:', message)
        await asyncio.sleep(4)

    async def serial_read(self) -> str:
        response = ''
        while self.serial.in_waiting > 0:
            response += self.serial.read(self.serial.in_waiting).decode('ascii')
            await asyncio.sleep(0.1)  # Short delay to ensure complete read
        return response.strip()

    def str_to_hex(self, string: str) -> str:
        return ' '.join(f'{ord(c):02X}' for c in string)

    def lora_end(self):
        if self.is_on:
            GPIO.cleanup()
            self.is_on = False
