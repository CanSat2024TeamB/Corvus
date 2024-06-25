import asyncio
import mavsdk 
from control.attitude import Attitude

class CompassHandler:
    def __init__(self, drone):
        self.drone = drone
        self.attitude = Attitude()
        asyncio.run(self.invoke_loop())

    async def update_attitude(self, euler, quaternion) -> None:
        """Update the attitude with the latest sensor data"""
        self.attitude.set_roll(euler.roll_deg)
        self.attitude.set_pitch(euler.pitch_deg)
        self.attitude.set_yaw(euler.yaw_deg)
        self.attitude.set_quaternion(quaternion.w, quaternion.x, quaternion.y, quaternion.z)
        return

    async def invoke_loop(self) -> None:
        async for euler, quaternion in zip(self.drone.telemetry.attitude_euler(), self.drone.telemetry.attitude_quaternion()):
            self.update_attitude(euler, quaternion)

    #############################################################以下がオープン
    def compass_attitude(self) -> Attitude:
        return self.attitude
    

    