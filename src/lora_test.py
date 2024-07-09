from lora.lora import Lora
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    Lora_ = Lora(drone)
    await Lora_.read()
    print(Lora_.msg_received)

if __name__ == '__main__':
    asyncio.run(main())