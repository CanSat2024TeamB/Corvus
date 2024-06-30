import bme680
import time

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
       
        self.interval = 1.0 


    
    def get_temperature(self):
        if self.sensor.get_sensor_data():
            return self.sensor.data.temperature
        else:
            return None
        time.sleep(self.interval)
    
    def get_pressure(self):
        if self.sensor.get_sensor_data():
            return self.sensor.data.pressure
        else:
            return None
        time.sleep(self.interval)
        
    def ave_pressure(self):
        pressure_lst = []
        for i in range(5):
            pre = self.get_pressure()
            pressure_lst.append(pre)

            if i == 4:
                ave_pre = sum(pressure_lst)/len(pressure_lst)

        return ave_pre
    
    def dif_ave_pressure(self,interval_def_ave_pressure):
        ave_pre_before = self.ave_pressure()
        time.sleep(interval_def_ave_pressure)
        ave_pre_after = self.ave_pressure()
        return ave_pre_after - ave_pre_before