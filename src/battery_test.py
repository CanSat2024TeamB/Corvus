from control.battery import Battery_watch
import asyncio
async def main():
    battery = Battery_watch()
    await asyncio.create_task(battery.invoke_loop())
    print(battery.voltage_v())
    print(battery.remaining_percent())
    print(battery.current_battery_a())

asyncio.run(main())