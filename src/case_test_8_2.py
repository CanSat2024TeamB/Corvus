import asyncio
import time
from pathlib import Path
from drone.drone_controller import DroneController
from case.case_handler import CaseHandler

async def main():
    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    case = CaseHandler(drone)

    global status 
    status = "outside"

    if status == "outside":
        case.judge_storage()
        status = "storage"
    if status == "storage":
        case.judge_release()
        status = "release"
    if status == "release":
        await case.judge_landing()
        status = "land"



if __name__ == "__main__":
    asyncio.run(main())