import sys
from pathlib import Path
from lora.lora import Lora
from drone.drone_controller import DroneController
import asyncio

async def main():
    dronecontroller = DroneController()
    drone = dronecontroller.get_drone_instance()
    lora = Lora(drone)
    print("Starting Lora...")
    await lora.lora_start()
    print("Lora started.")
    await asyncio.sleep(5)
    print("Setting sync...")
    await lora.lora_set_sync(72)
    print("Sync set.")
    await asyncio.sleep(5)
    print("Setting frequency...")
    await lora.lora_set_freq(922000000)
    print("Frequency set.")
    await asyncio.sleep(5)
    print("Setting spreading factor...")
    await lora.lora_set_sf(12)
    print("Spreading factor set.")
    await asyncio.sleep(5)
    print("Setting bandwidth...")
    await lora.lora_set_bw(125)
    print("Bandwidth set.")
    await asyncio.sleep(5)
    print("Setting power...")
    await lora.lora_set_pwr(20)
    print('Power set.')
    await asyncio.sleep(5)
    print("Saving settings...")
    await lora.lora_save()
    print("Settings saved.")
    await asyncio.sleep(5)
    print("Sending data...")
    count = 0
    while True:
        count += 1
        print(count)
        await lora.lora_send(123456)
        await asyncio.sleep(5)
    print("Ending Lora...")
    lora.lora_end()


# 実行するためのエントリーポイント
if __name__ == "__main__":
    asyncio.run(main())