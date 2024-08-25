import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from lora.lora import Lora
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    lora = Lora(drone)
    await lora.lora_start()
    await asyncio.sleep(5)
    await lora.lora_set_sync(72)
    await asyncio.sleep(5)
    await lora.lora_set_freq(922000000)
    await asyncio.sleep(5)
    await lora.lora_set_sf(7)
    await asyncio.sleep(5)
    await lora.lora_set_bw(125)
    await asyncio.sleep(5)
    await lora.lora_save()
    await asyncio.sleep(5)
    for i in range(10):
        await lora.lora_send(123456)
        await asyncio.sleep(5)
    lora.lora_end()

# 実行するためのエントリーポイント
if __name__ == "__main__":
    asyncio.run(main())