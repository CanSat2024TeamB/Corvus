import asyncio
from drone.drone_controller import DroneController
import RPi.GPIO as GPIO

def main():
    drone = DroneController()
    #GPIO.setmode(GPIO.BCM)
    GPIO.SETUP(7,GPIO.OUT)
    GPIO.OUTPUT(7,GPIO.LOW)
    print('set low')


    asyncio.sleep(20)
    print('start')
    drone.para_case_stand_nichrome()


if __name__ == "__main__":
    main()