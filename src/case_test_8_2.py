import asyncio
from drone.drone_controller import DroneController
from case.case_handler import CaseHandler

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    logger = dronecontroller.get_logger_instance()
    case = CaseHandler(drone,logger)

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