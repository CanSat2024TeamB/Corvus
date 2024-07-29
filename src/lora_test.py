from lora.lora import Lora
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    lora = Lora(drone)

    await lora.lora_reset()
    await lora.lora_set_sync(73)
    await lora.lora_set_freq(915000000)
    await lora.lora_set_sf(7)
    await lora.lora_set_bw(125)
    #await lora.lora_save()
    await lora.lora_write("Hello, LoRa!")
    lora.lora_end()

# 実行するためのエントリーポイント
if __name__ == "__main__":
    asyncio.run(main())