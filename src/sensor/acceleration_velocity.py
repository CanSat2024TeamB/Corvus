import mavsdk
from control.coordinates import Coordinates
import numpy as np  
import asyncio

class Acceleration_Velocity:
    def __init__(self, drone):
        self.drone = drone
        self.interval = 1.0

    async def get_velocity(self):
        velocity = await self.drone.telemetry.velocity_ned().__anext__()
        return np.array([velocity.x_m_s, velocity.y_m_s, velocity.z_m_s])

    async def get_acceleration(self):
        accel = await self.drone.telemetry.accelerationfrd().__anext__()
        return np.array([accel.forward_m_s2, accel.right_m_s2, accel.down_m_s2])

    async def ave_velocity(self):
        velocity_lst = []
        for i in range(5):
            vel = await self.get_velocity()
            print(vel)  # デバッグ用出力
            velocity_lst.append(vel)
            await asyncio.sleep(self.interval)

        ave_vel = sum(velocity_lst) / len(velocity_lst)
        return ave_vel

    async def dif_ave_velocity(self, interval_def_ave_velocity):
        ave_vel_before = await self.ave_velocity()
        await asyncio.sleep(interval_def_ave_velocity)
        ave_vel_after = await self.ave_velocity()
        return ave_vel_after - ave_vel_before
