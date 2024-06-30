import asyncio
import time
from drone.drone_controller import DroneController
from case.case_handler import CaseHandler


async def main():
    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    case = CaseHandler(drone)
    
    await dronecontroller.connect()
    async for imu in drone.telemetry.imu():
            a_x = imu.acceleration_frd.forward_m_s2
    print(a_x)
    print("done")


    

if __name__ == "__main__":
    asyncio.run(main())