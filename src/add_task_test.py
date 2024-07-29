import asyncio

class SimpleTaskManager:
    def __init__(self):
        self.task_group = None

    async def invoke_initial_tasks(self):
        async with asyncio.TaskGroup() as task_group:
            self.task_group = task_group  # TaskGroupの参照を保存
            task_group.create_task(self.print_message("Task 1: hello"))
            task_group.create_task(self.print_message("Task 2: world"))
            # TaskGroup が閉じるまで待機
            await asyncio.Future()  # 永続的に動作させる

    async def add_sequence_task(self, coro):
        if hasattr(self, 'task_group') and self.task_group:
            self.task_group.create_task(coro)
        else:
            print("No task group available to add the task.")

    async def print_message(self, message):
        while True:
            print(message)
            await asyncio.sleep(1)

async def main():
    manager = SimpleTaskManager()
    # Invoke initial tasks
    asyncio.create_task(manager.invoke_initial_tasks())

    # Wait a bit before adding the new task
    await asyncio.sleep(5)

    # Add a new task to the task group
    await manager.add_sequence_task(manager.print_message("Task 3: everyone"))

    # To ensure the program keeps running and you can see the outputs
    await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
