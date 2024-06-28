import asyncio
from drone.drone_controller import DroneController
import RPi.GPIO as GPIO
import time

BUTTON_PIN = 18  

def setup_gpio(pin):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def switch_pressed_callback(channel):
    print("Button was pressed!")
    DroneController().para_case_stand_nichrome()
    GPIO.cleanup()
    exit()

def wait_for_switch_press(pin):
    GPIO.add_event_detect(pin, GPIO.FALLING, callback=switch_pressed_callback, bouncetime=200)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    setup_gpio(BUTTON_PIN)
    wait_for_switch_press(BUTTON_PIN)