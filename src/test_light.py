from sensor import LightSensor
import time

if __name__ == "__main__":
    sensor = LightSensor()
    try:
        while True:
            value = sensor.read_value()
            print(f"Light Sensor Value: {value}")
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        sensor.close()