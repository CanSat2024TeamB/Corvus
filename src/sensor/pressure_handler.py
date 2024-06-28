import bme680
import asyncio

class PressureHandler:
    def __init__(self):
        try:
            self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
        except (RuntimeError, IOError):
            self.sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        self._initialize_sensor()

        self.pressure = 0.0
        self.temperature = 0.0
        

    
    def store_temperature(self):
        if self.sensor.get_sensor_data():
            self.temperature = self.sensor.data.temperature
        else:
            return None
    
    def store_pressure(self):
        if self.sensor.get_sensor_data():
            self.pressure = self.sensor.data.pressure
        else:
            return None
        
    ########################################################以下オープンにする

    async def invoke_loop(self):
        while True:
            self.get_pressure()
            self.get_temperature()
            asyncio.sleep(0.1)

    def  get_temperature(self):
        return self.temperature
    
    def get_pressure(self):
        return self.pressure
