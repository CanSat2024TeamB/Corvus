import asyncio
from drone.drone_controller import DroneController
import RPi.GPIO as GPIO
from case.case_handler import CaseHandler

async def main():
    nichrome_pin_no = 23

    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    case = CaseHandler(drone)
    await asyncio.sleep(20)
    print('start')
    case.para_case_stand_nichrome(nichrome_pin_no)
    print('done')
    print('cleanup done')


if __name__ == "__main__":
    asyncio.run(main())