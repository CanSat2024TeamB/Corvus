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

    async def lora_set_freq(self, freq_num):
        await self.serial_write(f'p2p set_freq {freq_num}')

    async def lora_set_sf(self, sf_num):
        await self.serial_write(f'p2p set_sf {sf_num}')

    async def lora_set_bw(self, bw_num):
        await self.serial_write(f'p2p set_bw {bw_num}')

    async def lora_save(self):
        await self.serial_write('p2p save')

    async def lora_write(self, message: str):
        await self.serial_write(f'p2p tx {message}')
        # Read and process two responses
        response1 = await self.serial_read()
        print('First response:', response1)
        if response1 == 'Ok':
            response2 = await self.serial_read()
            print('Second response:', response2)
        else:
            print('Invalid data format.')

    async def serial_write(self, message: str) -> None:
        msg_send = message + self.CRLF
        self.serial.write(msg_send.encode("ascii"))
        print('Sent:', message)
        await asyncio.sleep(1)  # Wait a moment before reading the response

    async def serial_read(self) -> str:
        response = ''
        while True:
            if self.serial.in_waiting > 0:
                chunk = self.serial.read(self.serial.in_waiting).decode('ascii')
                response += chunk
                # Check for end of response
                if '>>' in response:
                    break
            await asyncio.sleep(0.1)  # Short delay to ensure complete read
        return response.strip()

    def lora_end(self):
        if self.is_on:
            GPIO.cleanup()
            self.is_on = False

