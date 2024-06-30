from sensor.pressure_handler import PressureHandler
from sensor.acceleration_velocity import Acceleration_Velocity
from wire.wirehandler import WireHandler
import time

class CaseHandler:

    def __init__(self,drone):
        self.drone = drone
        self.pressure = PressureHandler()
        self.wirehandler = WireHandler()
        self.ac_vel = Acceleration_Velocity(self.drone)
        
        self.stable_pre_val = 1 ##1mで大体7hpaの差
        self.stable_vel_val = 0.1

        self.stable_judge_count = 5

        self.para_pin_no = 7
        self.para_duration = 5


    def judge_pressure_stable(self,interval_def_ave_pressure):
        stable_count = 0
        for i in range(self.stable_judge_count):
            def_pre = self.pressure.dif_ave_pressure(interval_def_ave_pressure)
            print(def_pre)####消す
            if abs(def_pre) <= self.stable_pre_val:
                stable_count += 1

            else:
                break    
        
        if stable_count == self.stable_judge_count:
            return True
        else:
            return False
        
    async def judge_velocity_stable(self, interval_def_ave_velocity):
        stable_count = 0
        for i in range(self.stable_judge_count):
            def_vel = await self.ac_vel.dif_ave_velocity(interval_def_ave_velocity)
            print(def_vel)  ## 値の確認のための出力、必要ない場合はコメントアウトする

            if np.all(np.abs(def_vel) <= self.stable_vel_val):
                stable_count += 1
            else:
                break

        if stable_count == self.stable_judge_count:
            return True
        else:
            return False
    
    def para_case_stand_nichrome(self):
        self.wirehandler.nichrome_cut(self.para_pin_no, self.para_duration)

        