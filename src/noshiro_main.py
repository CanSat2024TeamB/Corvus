import asyncio
from drone.drone_controller import DroneController
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from case.case_handler import CaseHandler
import logger.flight_log as flight_log
import time

async def main():
    drone = DroneController()
    case = CaseHandler(drone)
    
    logger = drone.get_logger_instance()
    config = ConfigManager()
    config_section = "NOSHIRO"
    nichrome_pin_no = config.read_int(config_section, "Nichrome_pin")

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

    countdown(10, logger)

    print(f"1para and case nichrome cut start")
    logger.write(f"1para and case nichrome cut start")

    case.para_case_stand_nichrome(nichrome_pin_no)

    print(f"1para and case nichrome cut end")
    logger.write(f"1para and case nichrome cut end")

    countdown(10, logger)

    print(f"1para and case nichrome cut start")
    logger.write(f"1para and case nichrome cut start")

    case.para_case_stand_nichrome(nichrome_pin_no)

    print(f"1para and case nichrome cut end")
    logger.write(f"1para and case nichrome cut end")

    case.nichrome_cleanup()
    await asyncio.sleep(20)

    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    asyncio.create_task(drone.invoke_sensor())
    #await drone.arm()
    await asyncio.sleep(5)


    position_manager = drone.get_position_manager_instance()
    flight_log.start(logger, position_manager)
    
    speed = 1.0
    first_lon = drone.position_manager.adjusted_coordinates_lon()
    first_lat = drone.position_manager.adjusted_coordinates_lat()
    hov_alt = 5
    target_coordinates_1 = Coordinates(first_lon,first_lat,hov_alt)
    target_coordinates_2 = Coordinates(140.05860198099998, 40.193250305, 5)
    
    await drone.add_sequence_task(drone.sequence_test_mission(speed,target_coordinates_1,target_coordinates_2))
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")
        logger.write("Main loop cancelled")
    
    flight_log.stop()

def countdown(seconds, logger):
    while seconds > 0:
        print(f"{seconds}秒")
        logger.write(f"{seconds}秒")
        time.sleep(1)
        seconds -= 1


if __name__ == "__main__":
    asyncio.run(main())