from wire.wirehandler import WireHandler
import asyncio

async def main():
    nichrome_pin_no = 23
    nichrome_pin_duration = 5
    wire = WireHandler()

    await asyncio.sleep(20)
    print('start')
    wire.nichrome_cut(nichrome_pin_no,nichrome_pin_duration)
    print('done')
    print('cleanup done')


if __name__ == "__main__":
    asyncio.run(main())