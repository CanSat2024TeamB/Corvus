from logger.logger import Logger
import asyncio

async def logger_test():
    logger = Logger()
    while True:
        await asyncio.sleep(1)
        logger.write("hello")

asyncio.run(logger_test())