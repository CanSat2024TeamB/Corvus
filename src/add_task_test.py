import asyncio

class SimpleTaskManager:
    def __init__(self):
        self.tasks = []

    async def invoke_initial_tasks(self):
        # 最初のタスクを `asyncio.gather` で実行
        self.tasks = [
            asyncio.create_task(self.print_message("Task 1: hello")),
            asyncio.create_task(self.print_message("Task 2: world")),
        ]

        # タスクの終了を待機
        await asyncio.gather(*self.tasks)

    async def add_sequence_task(self, coro):
        # 新しいタスクを追加
        new_task = asyncio.create_task(coro)
        self.tasks.append(new_task)

    async def print_message(self, message):
        while True:
            print(message)
            await asyncio.sleep(1)

async def main():
    manager = SimpleTaskManager()
    # Invoke initial tasks
    await manager.invoke_initial_tasks()

    # Wait a bit before adding the new task
    await asyncio.sleep(5)

    # Add a new task to the task group
    await manager.add_sequence_task(manager.print_message("Task 3: everyone"))

    # To ensure the program keeps running and you can see the outputs
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
