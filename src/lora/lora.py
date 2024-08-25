import RPi.GPIO as GPIO
import serial
import asyncio
import time

class Lora:
    def __init__(self, drone):
        self.drone = drone
        self.rst = 4
        self.CRLF = "\n\r"
        self.ser = None  # シリアルポートオブジェクトをメンバー変数として保持
        self.is_on = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst, GPIO.OUT)

    async def lora_start(self):
        try:
            self.ser = serial.Serial(port='/dev/ttyAMA0', baudrate=115200, bytesize=serial.EIGHTBITS, 
                                     parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            raise e

        #GPIO.output(self.rst, GPIO.LOW)
        #await asyncio.sleep(2)
        #GPIO.output(self.rst, GPIO.HIGH)
        #await asyncio.sleep(2)
        print("Lora power on")
        self.is_on = True

    async def lora_set_sync(self, sync_num):
        response = await self.send_and_receive(f'p2p set_sync {sync_num}')
        print('Response:', response)

    async def lora_set_freq(self, freq_num):
        response = await self.send_and_receive(f'p2p set_freq {freq_num}')
        print('Response:', response)

    async def lora_set_sf(self, sf_num):
        response = await self.send_and_receive(f'p2p set_sf {sf_num}')
        print('Response:', response)

    async def lora_set_bw(self, bw_num):
        response = await self.send_and_receive(f'p2p set_bw {bw_num}')
        print('Response:', response)

    async def lora_save(self):
        response = await self.send_and_receive('p2p save')
        print('Response:', response)

    async def lora_send(self,message):
        response = await self.send_and_receive(f'p2p tx {message}')
        print('Response:', response)

    async def send_and_receive(self, data, wait_time=2):
        try:
            # データを指定されたエンコード方式で送信
            self.ser.write(data.encode('ascii'))  
            self.ser.flush()
            await asyncio.sleep(wait_time)  # 受信するための待機時間を設定

            # 受信データを読み取ってデコード
            response = self.ser.read_all()
            response_decoded = response.decode('ascii').strip()  # 'ascii'で統一
            return response_decoded  # 正常時にはデコードされたレスポンスを返す
        except serial.SerialException as e:
            print(f"通信エラー: {e}")
            return ""

    def lora_end(self):
        if self.is_on:
            self.ser.close()  # シリアルポートを閉じる
            GPIO.cleanup()
            self.is_on = False