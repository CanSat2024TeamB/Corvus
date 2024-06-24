import asyncio
from mavsdk import System

class CompassHandler:
    def __init__(self, drone, Attitude):
        self.drone = drone
        self.attitude = Attitude()

    def get_attitude(self) -> dict:
        """Get current attitude"""
        return self.attitude.get_attitude()

    async def update_attitude(self) -> None:
        """Update the attitude with the latest sensor data"""
        async for euler, quaternion in zip(self.drone.telemetry.attitude_euler(), self.drone.telemetry.attitude_quaternion()):
            self.attitude.set_roll(euler.roll_deg)
            self.attitude.set_pitch(euler.pitch_deg)
            self.attitude.set_yaw(euler.yaw_deg)
            self.attitude.set_quaternion(quaternion.w, quaternion.x, quaternion.y, quaternion.z)
            print(self.attitude.get_attitude())

    async def invoke_loop(self) -> None:
        while True:
            await self.get_attitude_angle()
            await asyncio.sleep(0.01)