import asyncio
import mavsdk

import multiprocessing

from control.attitude import Attitude

class CompassHandler:
    def __init__(self, drone):
        self.drone = drone
        self.roll_deg = multiprocessing.Value("f", 0.0)
        self.pitch_deg = multiprocessing.Value("f", 0.0)
        self.yaw_deg = multiprocessing.Value("f", 0.0)
        self.quaternion = multiprocessing.Array("f", 4)

    async def update_attitude(self, euler, quaternion) -> None:
        """Update the attitude with the latest sensor data"""
        self.roll_deg.value = euler.roll_deg
        self.pitch_deg.value = euler.pitch_deg
        self.yaw_deg.value = euler.yaw_deg
        self.quaternion[0] = quaternion.w
        self.quaternion[1] = quaternion.x
        self.quaternion[2] = quaternion.y
        self.quaternion[3] = quaternion.z
        return
 #############################################################以下がオープン

    async def invoke_loop(self) -> None:
        while True:
            attitude_euler = self.drone.telemetry.attitude_euler()
            attitude_quaternion = self.drone.telemetry.attitude_quaternion()
            
            euler = await attitude_euler.__anext__()
            quaternion = await attitude_quaternion.__anext__()
            await self.update_attitude(euler, quaternion)
            await asyncio.sleep(0.05)


    def compass_attitude(self) -> Attitude:
        return Attitude(self.roll_deg.value, self.pitch_deg.value, self.yaw_deg.value, self.quaternion[0], self.quaternion[1], self.quaternion[2], self.quaternion[3])
    