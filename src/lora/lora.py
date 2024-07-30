import RPi.GPIO as GPIO
import serial
import asyncio

class Lora:
    def __init__(self, drone):
        self.drone = drone
        self.rst = 4
        self.power = 17
        self.CRLF = "\r\n"
        self.serial = None

        self.is_on = False
        self.counter = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)
        GPIO.setup(self.power, GPIO.OUT)

    async def lora_reset(self):
        """Start Lora"""
        GPIO.output(self.power, GPIO.HIGH)
        print('lora enable')
        try:
            self.serial = serial.Serial("/dev/ttyAMA0", 19200, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise e
        GPIO.output(self.rst, GPIO.LOW)
        await asyncio.sleep(2)
        GPIO.output(self.rst, GPIO.HIGH)
        await asyncio.sleep(2)
        print("Lora power on")
        self.is_on = True

    async def lora_set_sync(self, sync_num):
        await self.serial_write(f'p2p set_sync {sync_num}')
        response = await self.serial_read()
        print('Response:', response)

    async def lora_set_freq(self, freq_num):
        await self.serial_write(f'p2p set_freq {freq_num}')
        response = await self.serial_read()
        print('Response:', response)

    async def lora_set_sf(self, sf_num):
        await self.serial_write(f'p2p set_sf {sf_num}')
        response = await self.serial_read()
        print('Response:', response)

    async def lora_set_bw(self, bw_num):
        await self.serial_write(f'p2p set_bw {bw_num}')
        response = await self.serial_read()
        print('Response:', response)

    async def lora_save(self):
        await self.serial_write('p2p save')
        response = await self.serial_read()
        print('Response:', response)

    async def serial_write(self, message: str) -> None:
        cmd_send = f'> {message}' + self.CRLF
        self.serial.write(cmd_send.encode("ascii"))
        print('Sent:', cmd_send)
        await asyncio.sleep(1)  # Wait a moment before reading the response

    async def lora_write(self, message: str):
        await self.serial_write(f'p2p tx {message}')
        # Read and process two responses
        response1 = await self.serial_read()
        print('First response:', response1)
        if 'Ok' in response1:
            response2 = await self.serial_read()
            print('Second response:', response2)
        else:
            print('Invalid data format.')

    async def serial_read(self, timeout: float = 5.0) -> str:
        response = ''
        start_time = asyncio.get_event_loop().time()
        while True:
            if self.serial.in_waiting > 0:
                print('something')
                chunk = self.serial.read(self.serial.in_waiting).decode('ascii')
                response += chunk
                if '>>' in chunk:
                    break
            if asyncio.get_event_loop().time() - start_time > timeout:
                print('Read timeout')
                break
            await asyncio.sleep(0.1)  # Short delay to ensure complete read
        return response.strip()

    def lora_end(self):
        if self.is_on:
            GPIO.cleanup()
            self.is_on = False
