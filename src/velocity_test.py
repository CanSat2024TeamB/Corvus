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
    vel = await case.ac_vel.get_acceleration()
    print(vel)
    print("done")


    

if __name__ == "__main__":
    asyncio.run(main())