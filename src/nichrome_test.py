import asyncio
from drone.drone_controller import DroneController
import RPi.GPIO as GPIO

async def main():
    drone = DroneController()

    await asyncio.sleep(20)
    print('start')
    drone.para_case_stand_nichrome()
    print('done')
    GPIO.cleanup()
    print('cleanup done')


if __name__ == "__main__":
    main()