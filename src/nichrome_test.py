from wire.wirehandler import WireHandler
import asyncio

async def main():
    nichrome_pin_no_1 = 23
    nichrome_pin_no_2 = 25
    nichrome_pin_duration = 10
    wire = WireHandler()

    await asyncio.sleep(20)
    print('start')
    wire.nichrome_cut(nichrome_pin_no_1,nichrome_pin_duration)
    await asyncio.sleep(5)
    print('start')
    wire.nichrome_cut(nichrome_pin_no_2,nichrome_pin_duration)
    print('done')
    print('cleanup done')


if __name__ == "__main__":
    asyncio.run(main())