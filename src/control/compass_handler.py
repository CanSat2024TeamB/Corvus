import asyncio
import mavsdk


class CompassHandler:
    def __init__(self, drone, Attitude):
        self.drone = drone
        self.attitude = Attitude()

    async def get_attitude_angle(self) -> None:
        """Get angle from sensors"""
        async for angle in self.drone.telemetry.attitude_euler():
            self.attitude.set_roll(angle.roll_deg)
            self.attitude.set_pitch(angle.pitch_deg)
            self.attitude.set_yaw(angle.yaw_deg)
            print(self.attitude.get_attitude())

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