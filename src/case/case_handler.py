from sensor.pressure_handler import PressureHandler
from sensor.acceleration_velocity import Acceleration_Velocity
from sensor.light_handler import LightSensor
from wire.wirehandler import WireHandler
from drone.drone_controller import DroneController
from logger.logger import Logger
import time
import numpy as np

class CaseHandler:
    def __init__(self,drone):
        self.drone = drone

        self.light = LightSensor()
        self.pressure = PressureHandler()
        self.wirehandler = WireHandler()
        self.ac_vel = Acceleration_Velocity(self.drone)
        self.dronecontroller = DroneController()
        self.logger = self.dronecontroller.get_logger_instance()
        
        self.stable_pre_val = 1 ##1mで大体7hpaの差
        self.stable_vel_val = 0.1
        self.stable_judge_count = 5
        self.nichrome_duration = 10
        
        #収納判定用定数
        self.judge_storage_border_light = 300
        self.judge_storage_countmax = 10
        self.judge_storage_maxtime = 60 #300にする 
        self.judge_storage_sleep_time = 0.5
        self.light_counter = 0 #counterを設定

        #放出判定用定数
        self.judge_release_maxtime = 120 #去年はARLISSで3600を使った
        self.judge_release_lig_countmax = 12 
        self.judge_release_pre_countmax = 12
        self.judge_release_border_light = 500
        self.judge_release_sleep_time = 0.5
        
        #着地判定用定数
        self.judge_landing_maxtime = 120 #去年は1200



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
        
    def read_timer(self,time_sta): #時間計測用の関数
        time_end = time.perf_counter()# 時間計測終了
        self.tim = time_end - time_sta
        # print(tim)
        return self.tim
    
    def judge_storage(self):
        ##############################
        self.phase = "Outside"
        self.light_counter = 0 #counterを設定
        time_sta = time.perf_counter()
        ##############################
        while (self.read_timer(time_sta) <= self.judge_storage_maxtime):#300秒間実行

            if self.light.CANUSELIGHT == True:
                if self.light_counter < self.judge_storage_countmax:

                    light_value = self.light.get_light_value()

                    if light_value < self.judge_storage_border_light:#300以下であればcounterにプラス1
                        self.light_counter +=1
                        
                    else:
                        self.light_counter = 0#一回でも300以上であるならば外にいる判定
                        self.logger.write("Still Outside")
                        print("Still Outside") #あとで消す
                        
                else:#10回連続で暗い判定ができたら中であると判定
                    break
            else:
                self.logger.write("CAN NOT USE LIGHT")
                break
            
            print(self.light_counter) #あとで消す

            time.sleep(self.judge_storage_sleep_time)

        print("Storage Succeeded")
        self.logger.write("Storage Succeeded")
        self.phase = "Storage"
        self.message = "Storage"
        self.STORAGE = True
        return True
    
    def judge_release(self):
        ##############################
        self.light_counter = 0
        self.pressure_counter = 0
        time_sta = time.perf_counter()
        ##############################
        while (self.read_timer(time_sta) <= self.judge_release_maxtime):
            
            if self.light.CANUSELIGHT == False:
                self.light_counter = self.judge_release_lig_countmax
                time.sleep(5)

            if self.pressure.CANUSEPRESSURE == False:
                self.pressure_counter = self.judge_release_pre_countmax
                time.sleep(5)

            if (self.light_counter < self.judge_release_lig_countmax) and self.light.CANUSELIGHT == True:
                light_value = self.light.get_light_value()
                if light_value > self.judge_release_border_light:#明るい判定が出たらcounterに+1
                    self.light_counter +=1
            
                else:#10回たまらないうちに暗い判定が出たらリセット
                
                    self.light_counter = 0
                    self.logger.write("Light still low")
                    print("Light still low")


            if (self.pressure_counter < self.judge_release_pre_countmax) and self.pressure.CANUSEPRESSURE == True:
                Judge = self.judge_pressure_stable(10) #何秒とる？？

                if Judge == False:#pressureが変化していたら
                    self.pressure_counter +=1
                
            
                else:#10連続で変化を観測できなかったらリセット
                    self.pressure_counter = 0
                    self.logger.write("Disp pressure too stable or minus")
                    print("Disp pressure too stable or minus")
            
            if (self.light_counter >= self.judge_release_lig_countmax) and (self.pressure_counter >= self.judge_release_pre_countmax):
                break

            print(self.light_counter,self.pressure_counter)

            time.sleep(self.judge_release_sleep_time)

        self.logger.write("Release Succeeded")
        print("Release Succeeded")
        self.phase = "Released"
        self.message = "Released"
    

    async def judge_landing(self):
        ##############################
        time_sta = time.perf_counter()
        ##############################
        while True:
            self.logger.write("Pressure stability confirmation start")
            print(f"Pressure stability confirmation start")

            while (self.read_timer(time_sta) <= self.judge_landing_maxtime):
                if self.pressure.CANUSEPRESSURE == True:
                    if self.judge_pressure_stable(1): #5秒の測定の平均値を1秒ごとに計算
                        break
            
            self.logger.write("Pressure stability confirmed")
            print(f"Pressure stability confirmed")

            await self.dronecontroller.connect()
            self.logger.write("Velocity stability confirmation start")
            print(f"Velocity stability confirmation start")
            if await self.judge_velocity_stable(1):
                self.logger.write("Velocity stability cinfirmed")
                print(f"Velocity stability cinfirmed")
                break
            else:
                self.logger.write("Velocity not stable.restart")
                print(f"Velocity not stable.restart")
        
        self.logger.write("Landing Succeeded")
        print("Landing Succeeded")
        self.phase = "Land"
        self.message = "Land"


    def para_case_stand_nichrome(self,nichrome_pin_no):
        self.wirehandler.nichrome_cut(nichrome_pin_no, self.nichrome_duration)


    def nichrome_cleanup(self):
        self.wirehandler.cleanup()    