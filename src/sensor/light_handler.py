import spidev
import time

class LightSensor:
    def __init__(self, spi_bus=0, spi_device=0):
        self.spi_bus = spi_bus
        self.spi_device = spi_device
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1000000

    def read_light_value(self):
        try:
            # SPI通信で値を読み込む
            resp = self.spi.xfer2([0x68, 0x00])
            light_value = ((resp[0] << 8) + resp[1]) & 0x3FF
            return light_value
        except Exception as e:
            print(f"Error reading light intensity: {e}")
            return None

    def close(self):
        # SPI通信を終了する
        self.spi.close()

# # 使用例
# if __name__ == "__main__":
#     sensor = LightSensor()
#     try:
#         while True:
#             value = sensor.read_value()
#             print(f"Light Sensor Value: {value}")
#             time.sleep(1)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         sensor.close()
