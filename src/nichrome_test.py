import asyncio
from drone.drone_controller import DroneController

def main():
    drone = DroneController()

    asyncio.sleep(20)
    print('start')
    drone.para_case_stand_nichrome()


if __name__ == "__main__":
    main()