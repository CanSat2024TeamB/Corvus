import asyncio
from drone.drone_controller import DroneController
from control.coordinates import Coordinates
from config.config_manager import ConfigManager
from case.case_handler import CaseHandler
import logger.flight_log as flight_log
import time

async def sequence(drone: DroneController, speed: float, target_coordinates: Coordinates, goal_radius: float):
    logger = drone.get_logger_instance()
    logger.write("taking off")
    await drone.flight_controller.takeoff(target_coordinates.altitude())
    logger.write("finished taking off")
    await drone.flight_controller.hovering(5)
    logger.write("going to the target position")
    await drone.flight_controller.go_to_location(speed, target_coordinates, goal_radius)
    logger.write("start precise landing")
    result = await drone.flight_controller.offboard_precise_land()
    if not result:
        await drone.flight_controller.go_to_location(speed, target_coordinates, goal_radius)
        logger.write("starting vertical land")
        await drone.flight_controller.land()
    logger.write("landed")

async def main():
    drone: DroneController = DroneController()
    case: CaseHandler = CaseHandler(drone)
    
    logger = drone.get_logger_instance()
    lora = drone.get_lora_instance()

    config: ConfigManager = ConfigManager()
    config_section = "ARLISS"
    nichrome_pin_no = config.read_int(config_section, "NichromePin")

    status = config.read(config_section, "Status")

    logger.write("Starting Lora...")
    await lora.lora_start()
    logger.write("Lora started.")
    await asyncio.sleep(5)
    logger.write("Setting sync...")
    await lora.lora_set_sync(72)
    logger.write("Sync set.")
    await asyncio.sleep(5)
    logger.write("Setting frequency...")
    await lora.lora_set_freq(922000000)
    logger.write("Frequency set.")
    await asyncio.sleep(5)
    logger.write("Setting spreading factor...")
    await lora.lora_set_sf(12)
    logger.write("Spreading factor set.")
    await asyncio.sleep(5)
    logger.write("Setting bandwidth...")
    await lora.lora_set_bw(125)
    logger.write("Bandwidth set.")
    await asyncio.sleep(5)
    logger.write("Setting power...")
    await lora.lora_set_pwr(20)
    logger.write('Power set.')
    await asyncio.sleep(5)
    logger.write("Saving settings...")
    await lora.lora_save()
    logger.write("Settings saved.")
    await asyncio.sleep(5)

    if status == "outside":
       case.judge_storage()
       config.write(config_section, "Status", "storage")
       await lora.lora_send('storage')

    if status == "storage":
        case.judge_release()
        config.write(config_section, "Status", "release")
        await lora.lora_send('release')

    if status == "release":
        countdown(30, logger)
        await case.judge_landing()
        config.write(config_section, "Status", "land")
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
    
    speed = config.read_float(config_section, "Speed")
    hov_alt = config.read_float(config_section, "HovAlt")
    target_lon = config.read_float(config_section, "TargetLon")
    target_lat = config.read_float(config_section, "TargetLat")
    goal_radius = config.read_float(config_section, "GoalRadius")
    target_coordinates_2 = Coordinates(target_lon, target_lat, hov_alt)
    
    await drone.add_sequence_task(sequence(drone, speed, target_coordinates_2, goal_radius))
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
        logger.write(f"{seconds} seconds")
        time.sleep(1)
        seconds -= 1


if __name__ == "__main__":
    asyncio.run(main())