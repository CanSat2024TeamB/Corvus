import asyncio
from drone.drone_controller import DroneController
from control.coordinates import Coordinates
from pathlib import Path
from config.config_manager import ConfigManager
from case.case_handler import CaseHandler
import logger.flight_log as flight_log
import time

async def sequence_test_goto(drone: DroneController, speed, target_coordinates: Coordinates):
    logger = drone.get_logger_instance()
    print("arming")
    logger.write("arming")
    await drone.arm()
    print("taking off...")
    logger.write("taking off...")
    await drone.flight_controller.takeoff(target_coordinates.altitude())
    print('reached')
    logger.write('reached')
    await drone.flight_controller.hovering(5)
    print('goto started')
    logger.write('goto started')
    await drone.flight_controller.go_to_location(speed, target_coordinates, 0.5)
    print('goto finished start hovering')
    logger.write('goto finished start hovering')
    await drone.flight_controller.hovering(2)
    print('hovering finished start landing')
    logger.write('hovering finished start landing')
    await drone.flight_controller.land()
    print("landed")
    logger.write("landed")

async def main():
    drone = DroneController()
    case = CaseHandler(drone)
    
    logger = drone.get_logger_instance()
    lora = drone.get_lora_instance()

    config = ConfigManager()
    config_section = "NOSHIRO"
    nichrome_pin_no = config.read_int(config_section, "Nichrome_pin")

    global status 
    status = "outside"

    await lora.lora_start()
    await asyncio.sleep(5)
    await lora.lora_set_sync(72)
    await asyncio.sleep(5)
    await lora.lora_set_freq(922000000)
    await asyncio.sleep(5)
    await lora.lora_set_sf(7)
    await asyncio.sleep(5)
    await lora.lora_set_bw(125)
    await asyncio.sleep(5)
    await lora.lora_save()
    await asyncio.sleep(5)
    await lora.lora_send('lora ok')
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
    await lora.lora_send('nichrome_end')
    countdown(60, logger)

    #config_path: str = Path(__file__).resolve().parent.parent.joinpath("assets/config/config.ini")
    #config = ConfigManager(config_path)
    asyncio.create_task(drone.invoke_sensor())
    #await drone.arm()
    await asyncio.sleep(5)


    position_manager = drone.get_position_manager_instance()
    flight_log.start(logger, position_manager)
    
    speed = 4.0
    hov_alt = 5
    target_coordinates_2 = Coordinates(139.987197098,40.142462332,hov_alt)
    
    
    await drone.add_sequence_task(sequence_test_goto(drone, speed, target_coordinates_2))
    try:
        await asyncio.Future()
    except asyncio.CancelledError:
        print("Main loop cancelled")
        logger.write("Main loop cancelled")

    # try:
    #     await drone.add_sequence_task(drone.sequence_test_mission(speed,target_coordinates_1,target_coordinates_2))
    # except asyncio.CancelledError:
    #     print("Main loop cancelled")
    #     logger.write("Main loop cancelled")
    
    flight_log.stop()

    print("sequence ended")
    logger.write("sequence ended")

def countdown(seconds, logger):
    while seconds > 0:
        print(f"{seconds}秒")
        logger.write(f"{seconds}秒")
        time.sleep(1)
        seconds -= 1


if __name__ == "__main__":
    asyncio.run(main())