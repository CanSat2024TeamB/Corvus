import asyncio
from threading import Thread
import time

class SimpleTaskManager:
    async def invoke_initial_tasks(self):
        await asyncio.gather(
            self.print_message("Task 1: hello"),
            self.print_message("Task 2: world")
        )

    async def print_message(self, message):
        while True:
            print(message)
            await asyncio.sleep(1)

async def main():
    manager = SimpleTaskManager()
    event_loop = asyncio.get_event_loop()

    asyncio.run_coroutine_threadsafe(manager.invoke_initial_tasks(), event_loop)

    # Wait a bit before adding the new task
    await asyncio.sleep(5)

    asyncio.run_coroutine_threadsafe(manager.print_message("Task 3: everyone"), event_loop)

    # To ensure the program keeps running and you can see the outputs
    await asyncio.sleep(10)

    event_loop.call_soon_threadsafe(event_loop.stop)

if __name__ == "__main__":
    asyncio.run(main())