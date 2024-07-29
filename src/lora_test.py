from lora.lora import Lora
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    lora = Lora(drone)
    await lora.change_mode()
    await lora.lora_write()

if __name__ == '__main__':
    asyncio.run(main())