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
    lora = drone.get_lora_instance()

    config = ConfigManager()
    config_section = "ARLISS"
    nichrome_pin_no = config.read_int(config_section, "Nichrome_pin")

    global status 
    status = "outside"

    print("Starting Lora...")
    await lora.lora_start()
    print("Lora started.")
    await asyncio.sleep(5)
    print("Setting sync...")
    await lora.lora_set_sync(72)
    print("Sync set.")
    await asyncio.sleep(5)
    print("Setting frequency...")
    await lora.lora_set_freq(922000000)
    print("Frequency set.")
    await asyncio.sleep(5)
    print("Setting spreading factor...")
    await lora.lora_set_sf(12)
    print("Spreading factor set.")
    await asyncio.sleep(5)
    print("Setting bandwidth...")
    await lora.lora_set_bw(125)
    print("Bandwidth set.")
    await asyncio.sleep(5)
    print("Setting power...")
    await lora.lora_set_pwr(20)
    print('Power set.')
    await asyncio.sleep(5)
    print("Saving settings...")
    await lora.lora_save()
    print("Settings saved.")
    await asyncio.sleep(5)

    if status == "outside":
       case.judge_storage()
       status = "storage"
       await lora.lora_send('storage')

    if status == "storage":
        case.judge_release()
        status = "release"
        await lora.lora_send('release')

    if status == "release":
        countdown(30,logger)
        await case.judge_landing()
        status = "land"
        await lora.lora_send('land')

    countdown(10, logger)

    logger.write(f"1para and case nichrome cut start")

    case.para_case_stand_nichrome(nichrome_pin_no)

    logger.write(f"1para and case nichrome cut end")

    countdown(10, logger)

    logger.write(f"1para and case nichrome cut start")

    case.para_case_stand_nichrome(nichrome_pin_no)

    logger.write(f"1para and case nichrome cut end")

    case.nichrome_cleanup()
    await lora.lora_send('nichrome_end')
    countdown(60, logger)

    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    asyncio.create_task(drone.invoke_sensor())
    #await drone.arm()
    await asyncio.sleep(5)


    position_manager = drone.get_position_manager_instance()
    flight_log.start(logger, position_manager)
    
    speed = 8.2
    hov_alt = 5
    target_coordinates_2 = Coordinates(139.987197098,40.142462332,hov_alt)
    
    
    await drone.add_sequence_task(drone.sequence_test_goto(speed, target_coordinates_2))
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        logger.write("Main loop cancelled")

    # try:
    #     await drone.add_sequence_task(drone.sequence_test_mission(speed,target_coordinates_1,target_coordinates_2))
    # except asyncio.CancelledError:
    #     print("Main loop cancelled")
    #     logger.write("Main loop cancelled")
    
    flight_log.stop()

    logger.write("sequence ended")

def countdown(seconds, logger):
    while seconds > 0:
        logger.write(f"{seconds}秒")
        time.sleep(1)
        seconds -= 1


if __name__ == "__main__":
    asyncio.run(main())