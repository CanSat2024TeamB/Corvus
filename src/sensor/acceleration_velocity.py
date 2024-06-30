import mavsdk
from control.coordinates import Coordinates
import numpy as np  
import time

class Acceleration_Velocity():
    def __init__(self,drone):
        self.drone = drone

        self.interval = 1.0

    async def get_velocity(self):
        velocity = await self.drone.telemetry.velocitybody().__anext__()
        return np.array([velocity.x_m_s,velocity.y_m_s,velocity.z_m_s])

    async def get_acceleration(self):
        accel = await self.drone.telemetry.accelerationfrd()
        return np.array([accel.forward_m_s2, accel.right_m_s2, accel.down_m_s2])
    
    def ave_velocity(self):
        velocity_lst = []
        for i in range(5):
            vel = self.get_velocity()
            velocity_lst.append(vel)
            time.sleep(self.interval)

            if i == 4:
                ave_vel = sum(velocity_lst)/len(velocity_lst)

        return ave_vel
    
    def dif_ave_velocity(self,interval_def_ave_velocity):
        ave_vel_before = self.ave_velocity()
        time.sleep(interval_def_ave_velocity)
        ave_vel_after = self.ave_velocity()
        return ave_vel_after - ave_vel_before