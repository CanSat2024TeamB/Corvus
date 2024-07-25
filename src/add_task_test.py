import asyncio

class SimpleTaskManager:
    def __init__(self):
        self.task_group = None

    async def invoke_initial_tasks(self):
        async with asyncio.TaskGroup() as task_group:
            self.task_group = task_group  # TaskGroupの参照を保存
            task_group.create_task(self.print_message("Task 1: hello"))
            task_group.create_task(self.print_message("Task 2: world"))
            await asyncio.sleep(10)  # タスクが動作する時間を確保

    async def add_sequence_task(self, coro):
        if hasattr(self, 'task_group') and self.task_group:
            self.task_group.create_task(coro)

    async def print_message(self, message):
        while True:
            print(message)
            await asyncio.sleep(1)

async def main():
    manager = SimpleTaskManager()
    await manager.invoke_initial_tasks()

    await asyncio.sleep(5)  # 5秒後に新しいタスクを追加
    await manager.add_sequence_task(manager.print_message("Task 3: everyone"))

if __name__ == "__main__":
    asyncio.run(main())
